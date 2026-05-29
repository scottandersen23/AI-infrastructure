# Kubernetes AI Platform Architecture

## Component Diagram

```mermaid
flowchart TB
    User[User / Client]
    Ingress[nginx Ingress<br/>ai-platform.local]
    API[API Service<br/>Deployment + Service]
    Worker[Worker Service<br/>Deployment]
    LLM[LLM Service<br/>Deployment + Service]
    Postgres[(Postgres + pgvector<br/>PVC)]
    Redis[(Redis Queue)]
    Observability[Observability Service<br/>OTLP + Dashboard]
    Dashboard[Dashboard Service]
    HPA[Horizontal Pod Autoscalers]

    User --> Ingress
    Ingress --> API
    Ingress --> LLM
    Ingress --> Observability
    Ingress --> Dashboard
    API --> LLM
    API --> Postgres
    API --> Redis
    Worker --> Redis
    Worker --> Postgres
    API --> Observability
    LLM --> Observability
    HPA -. scales .-> API
    HPA -. scales .-> Worker
    HPA -. scales .-> LLM
```

## Request Flow

```text
Ingress
  -> API service
      -> LLM service
      -> Vector database / Postgres
      -> Redis queue
      -> Observability collector
```

## Operational Boundaries

| Boundary           | Kubernetes Object                                  |
| ------------------ | -------------------------------------------------- |
| Routing            | Ingress, Services                                  |
| Runtime isolation  | Deployments, Pods                                  |
| Configuration      | ConfigMap                                          |
| Sensitive settings | Secret                                             |
| Persistence        | PersistentVolumeClaim                              |
| Scaling            | HorizontalPodAutoscaler                            |
| Safety             | Resource requests/limits, probes, network policies |
