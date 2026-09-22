CREATE TABLE places (
  place_id      TEXT PRIMARY KEY,
  place_name    TEXT,
  centroid_lat  DOUBLE PRECISION NOT NULL,
  centroid_lon  DOUBLE PRECISION NOT NULL,
  polygon_geojson JSONB NOT NULL,
  area_hectares DOUBLE PRECISION,
  state         TEXT,
  district      TEXT,
  first_visit_utc TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_visit_utc  TIMESTAMPTZ NOT NULL DEFAULT now(),
  visit_count   INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE visits (
  visit_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  place_id      TEXT REFERENCES places(place_id),
  visit_timestamp_utc TIMESTAMPTZ NOT NULL DEFAULT now(),
  local_date    DATE,
  local_time    TIME,
  visit_number_for_place INTEGER,
  days_since_previous_visit INTEGER
);

CREATE TABLE observations (
  obs_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  visit_id      UUID REFERENCES visits(visit_id),
  place_id      TEXT REFERENCES places(place_id),
  scene_date    DATE,
  ndvi          DOUBLE PRECISION,
  ndvi_source   TEXT NOT NULL,
  cloud_pct     DOUBLE PRECISION,
  temperature_c DOUBLE PRECISION,
  humidity_pct  DOUBLE PRECISION,
  rain_mm_24h   DOUBLE PRECISION,
  rain_mm_7d    DOUBLE PRECISION,
  heat_stress_flag BOOLEAN,
  soil_moisture DOUBLE PRECISION,
  weather_source TEXT NOT NULL,
  capacitive_pf DOUBLE PRECISION,
  acoustic_val  DOUBLE PRECISION,
  sensor_source TEXT NOT NULL DEFAULT 'not_connected',
  provenance    JSONB NOT NULL
);

CREATE TABLE labels (
  label_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  place_id      TEXT REFERENCES places(place_id),
  visit_id      UUID REFERENCES visits(visit_id),
  label_type    TEXT NOT NULL,
  label_value   TEXT NOT NULL,
  label_source  TEXT NOT NULL,
  created_utc   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE predictions (
  prediction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  visit_id      UUID REFERENCES visits(visit_id),
  model_version TEXT NOT NULL,
  target        TEXT NOT NULL,
  predicted_value TEXT,
  calibrated_probability DOUBLE PRECISION,
  abstained     BOOLEAN NOT NULL DEFAULT false,
  created_utc   TIMESTAMPTZ NOT NULL DEFAULT now()
);
