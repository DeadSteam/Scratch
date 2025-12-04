-- Enable UUID extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Films
CREATE TABLE IF NOT EXISTS films (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    coating_name VARCHAR(100),
    coating_thickness DOUBLE PRECISION
);

-- Equipment configs
CREATE TABLE IF NOT EXISTS equipment_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    head_type VARCHAR(100),
    description TEXT
);

-- Experiments (user_id has no FK - users are in separate DB)
CREATE TABLE IF NOT EXISTS experiments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    film_id UUID NOT NULL REFERENCES films(id) ON DELETE CASCADE,
    config_id UUID NOT NULL REFERENCES equipment_configs(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    name VARCHAR(200),
    date TIMESTAMP WITH TIME ZONE DEFAULT now(),
    rect_coords DOUBLE PRECISION[],
    weight DOUBLE PRECISION,
    has_fabric BOOLEAN NOT NULL DEFAULT FALSE,
    scratch_results JSONB
);

-- Experiment images
CREATE TABLE IF NOT EXISTS experiment_images (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    experiment_id UUID NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    image_data BYTEA NOT NULL,
    passes INTEGER DEFAULT 0
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_films_name ON films(name);
CREATE INDEX IF NOT EXISTS idx_econfigs_name ON equipment_configs(name);
CREATE INDEX IF NOT EXISTS idx_experiments_user_id ON experiments(user_id);
CREATE INDEX IF NOT EXISTS idx_experiment_images_experiment_id ON experiment_images(experiment_id);
