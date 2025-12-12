-- PostgreSQL/PostGIS initialization script
-- This script runs automatically when the database container is first created

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Enable UUID extension for UUID primary keys
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create spatial reference systems if not exists
-- WGS 84 (SRID 4326) - standard GPS coordinate system
-- This is typically already included in PostGIS but ensuring it exists

-- Grant privileges to the application user
GRANT ALL PRIVILEGES ON DATABASE ingazo TO ingazo;

-- Log success
DO $$
BEGIN
    RAISE NOTICE 'PostGIS extensions initialized successfully';
END $$;

