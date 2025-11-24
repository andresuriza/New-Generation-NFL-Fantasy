-- Migration script to update designacion_lesion enum values
-- This script updates the enum to use single-character values that match our Python implementation

-- First, we need to add the new enum values
ALTER TYPE designacion_lesion ADD VALUE IF NOT EXISTS 'O';
ALTER TYPE designacion_lesion ADD VALUE IF NOT EXISTS 'D';
ALTER TYPE designacion_lesion ADD VALUE IF NOT EXISTS 'Q';
ALTER TYPE designacion_lesion ADD VALUE IF NOT EXISTS 'P';
ALTER TYPE designacion_lesion ADD VALUE IF NOT EXISTS 'FP';
ALTER TYPE designacion_lesion ADD VALUE IF NOT EXISTS 'IR';
ALTER TYPE designacion_lesion ADD VALUE IF NOT EXISTS 'PUP';
ALTER TYPE designacion_lesion ADD VALUE IF NOT EXISTS 'SUS';

-- Update any existing data (if any) to use the new values
-- Note: This assumes there's no existing data, but we include mapping just in case
UPDATE noticias_jugadores 
SET designacion = CASE 
    WHEN designacion = 'Out' THEN 'O'
    WHEN designacion = 'Doubtful' THEN 'D'
    WHEN designacion = 'Questionable' THEN 'Q'
    WHEN designacion = 'Healthy' THEN 'P'
    WHEN designacion = 'Injured_Reserve' THEN 'IR'
    WHEN designacion = 'Physically_Unable_to_Perform' THEN 'PUP'
    WHEN designacion = 'Did_Not_Participate' THEN 'SUS'
    ELSE designacion
END
WHERE designacion IN ('Out', 'Doubtful', 'Questionable', 'Healthy', 'Injured_Reserve', 'Physically_Unable_to_Perform', 'Did_Not_Participate');

-- Note: PostgreSQL doesn't support removing enum values directly in a transaction
-- The old values will remain in the enum type but won't be used
-- If needed, a full enum recreation would require more complex steps

-- Verify the update
SELECT enumlabel FROM pg_enum WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'designacion_lesion') ORDER BY enumlabel;