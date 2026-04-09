# pi/telemetry/

UART parser, CSV logger, and operator dashboard for telemetry coming from the custom MCU board.

> Populated in **Phase 1** (Pi-direct sensor logging) and extended in **Phase 2** (frame parser for the MCU link).

Expected layout:

```
telemetry/
├── parser.py           (frame decoder for MCU UART link)
├── logger.py           (CSV writer)
├── dashboard/          (FastAPI / Streamlit app)
├── config.yaml
└── sample_data/        (small representative datasets, committed)
```

Frame format spec: [`../../docs/05-firmware-architecture.md#uart-telemetry-frame-format-draft`](../../docs/05-firmware-architecture.md)
