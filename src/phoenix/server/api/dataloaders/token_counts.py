from collections import defaultdict
from datetime import datetime
from typing import Any, Literal, Optional

from cachetools import LFUCache, TTLCache
from sqlalchemy import Select, func, select
from sqlalchemy.sql.functions import coalesce
from strawberry.dataloader import AbstractCache, DataLoader
from typing_extensions import TypeAlias

from phoenix.db import models
from phoenix.server.api.dataloaders.cache import TwoTierCache
from phoenix.server.api.input_types.TimeRange import TimeRange
from phoenix.server.types import DbSessionFactory
from phoenix.trace.dsl import SpanFilter

Kind: TypeAlias = Literal["prompt", "completion", "total"]
ProjectRowId: TypeAlias = int
TimeInterval: TypeAlias = tuple[Optional[datetime], Optional[datetime]]
FilterCondition: TypeAlias = Optional[str]
TokenCount: TypeAlias = int

Segment: TypeAlias = tuple[TimeInterval, FilterCondition]
Param: TypeAlias = tuple[ProjectRowId, Kind]

Key: TypeAlias = tuple[Kind, ProjectRowId, Optional[TimeRange], FilterCondition]
Result: TypeAlias = TokenCount
ResultPosition: TypeAlias = int
DEFAULT_VALUE: Result = 0


def _cache_key_fn(key: Key) -> tuple[Segment, Param]:
    kind, project_rowid, time_range, filter_condition = key
    interval = (
        (time_range.start, time_range.end) if isinstance(time_range, TimeRange) else (None, None)
    )
    return (interval, filter_condition), (project_rowid, kind)


_Section: TypeAlias = ProjectRowId
_SubKey: TypeAlias = tuple[TimeInterval, FilterCondition, Kind]


class TokenCountCache(
    TwoTierCache[Key, Result, _Section, _SubKey],
):
    def __init__(self) -> None:
        super().__init__(
            # TTL=3600 (1-hour) because time intervals are always moving forward, but
            # interval endpoints are rounded down to the hour by the UI, so anything
            # older than an hour most likely won't be a cache-hit anyway.
            main_cache=TTLCache(maxsize=64, ttl=3600),
            sub_cache_factory=lambda: LFUCache(maxsize=2 * 2 * 3),
        )

    def _cache_key(self, key: Key) -> tuple[_Section, _SubKey]:
        (interval, filter_condition), (project_rowid, kind) = _cache_key_fn(key)
        return project_rowid, (interval, filter_condition, kind)


class TokenCountDataLoader(DataLoader[Key, Result]):
    def __init__(
        self,
        db: DbSessionFactory,
        cache_map: Optional[AbstractCache[Key, Result]] = None,
    ) -> None:
        super().__init__(
            load_fn=self._load_fn,
            cache_key_fn=_cache_key_fn,
            cache_map=cache_map,
        )
        self._db = db

    async def _load_fn(self, keys: list[Key]) -> list[Result]:
        results: list[Result] = [DEFAULT_VALUE] * len(keys)
        arguments: defaultdict[
            Segment,
            defaultdict[Param, list[ResultPosition]],
        ] = defaultdict(lambda: defaultdict(list))
        for position, key in enumerate(keys):
            segment, param = _cache_key_fn(key)
            arguments[segment][param].append(position)
        async with self._db() as session:
            for segment, params in arguments.items():
                stmt = _get_stmt(segment, *params.keys())
                data = await session.stream(stmt)
                async for project_rowid, prompt, completion, total in data:
                    for position in params[(project_rowid, "prompt")]:
                        results[position] = prompt
                    for position in params[(project_rowid, "completion")]:
                        results[position] = completion
                    for position in params[(project_rowid, "total")]:
                        results[position] = total
        return results


def _get_stmt(
    segment: Segment,
    *params: Param,
) -> Select[Any]:
    (start_time, end_time), filter_condition = segment
    prompt = coalesce(func.sum(models.Span.llm_token_count_prompt), 0)
    completion = coalesce(func.sum(models.Span.llm_token_count_completion), 0)
    total = prompt + completion
    pid = models.Trace.project_rowid
    stmt: Select[Any] = (
        select(
            pid,
            prompt.label("prompt"),
            completion.label("completion"),
            total.label("total"),
        )
        .join_from(models.Trace, models.Span)
        .group_by(pid)
    )
    if start_time:
        stmt = stmt.where(start_time <= models.Span.start_time)
    if end_time:
        stmt = stmt.where(models.Span.start_time < end_time)
    if filter_condition:
        sf = SpanFilter(filter_condition)
        stmt = sf(stmt)
    stmt = stmt.where(pid.in_([rowid for rowid, _ in params]))
    return stmt
