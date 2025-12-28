# my-scalping-kabu-station-example

## Environment variables

- `HISTORY_PATH` (optional): History directory or base CSV path, default `data/history`
- `WS_URL` (optional): WebSocket endpoint URL
- `WS_API_KEY` (optional): WebSocket API key sent as `X-API-KEY`
- `FEATURE_SPEC_JSON` (optional): JSON string for FeatureSpec fields (`version`, `eps`, `params`, `features`)
- `FEATURE_SPEC_VERSION` (optional): FeatureSpec version, default `ob10_v1`
- `FEATURE_SPEC_EPS` (optional): FeatureSpec epsilon, default `1e-9`
- `FEATURE_SPEC_PARAMS_JSON` (optional): JSON string for FeatureSpec `params`
- `RISK_MAX_POSITION` (optional): max position size, default `1.0`
- `RISK_STOP_LOSS` (optional): stop loss in pips, default `1.0`
- `RISK_TAKE_PROFIT` (optional): take profit in pips, default `1.0`
- `RISK_COOLDOWN_SECONDS` (optional): cooldown seconds, default `0.0`
- `RISK_LOSS_CUT_PIPS` (optional): loss cut pips, default `0.0`
