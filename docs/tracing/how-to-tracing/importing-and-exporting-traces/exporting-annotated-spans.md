# Exporting Annotated Spans

Span annotations can be an extremely valuable basis for improving your application. The Phoenix client provides useful ways to pull down spans and their associated annotations. This information can be used to:

* build new LLM judges
* form the basis for new datasets
* help identify ideas for improving your application

### Pulling Spans

```python
from phoenix.client import Client

client = Client()

spans = client.spans.get_spans_dataframe(
    project_identifier="default",  # you can also pass a project id
)
```

If you only want the spans that contain a specific annotation, you can pass in a query that filters on annotation names, scores, or labels.

```python
from phoenix.client import Client
from phoenix.client.types.span import SpanQuery

client = Client()
query = SpanQuery().where("annotations['correctness']")

spans = client.spans.get_spans_dataframe(
    query=query,
    project_identifier="default",  # you can also pass a project id
)
```

The queries can also filter by annotation scores and labels.

```python
from phoenix.client import Client
from phoenix.client.types.span import SpanQuery

client = Client()
query = SpanQuery().where("annotations['correctness'].score == 1")
# query = SpanQuery().where("annotations['correctness'].label == 'correct'")

spans = client.spans.get_spans_dataframe(
    query=query,
    project_identifier="default",  # you can also pass a project id
)
```

This spans dataframe can be used to pull associated annotations.

```python
annotations = client.spans.get_span_annotations_dataframe(
    spans_dataframe=spans,
    project_identifier="default",
)
```

Instead of an input dataframe, you can also pass in a list of ids:

```python
annotations = client.spans.get_span_annotations_dataframe(
    span_ids=list[spans.index],
    project_identifier="default",
)
```

The annotations and spans dataframes can be easily joined to produce a one-row-per-annotation dataframe that can be used to analyze the annotations!

```python
annotations.join(spans, how="left")
```
