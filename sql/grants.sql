-- Rerun this after every CREATE OR REPLACE of the pipeline (02_pipeline.ipynb),
-- since CREATE OR REPLACE VIEW/TABLE drops existing grants.

-- Dashboard / warehouse access for the user running the demo.
GRANT USE CATALOG ON CATALOG workspace TO `jalisyed@gmail.com`;
GRANT USE SCHEMA ON SCHEMA workspace.r5_drybuild2 TO `jalisyed@gmail.com`;
GRANT SELECT ON SCHEMA workspace.r5_drybuild2 TO `jalisyed@gmail.com`;

-- Databricks App service principal (app "r5-drybuild2-retail", created Phase 4).
GRANT USE CATALOG ON CATALOG workspace TO `804a3ed5-0f8d-494c-99e5-93f4c75fc644`;
GRANT USE SCHEMA ON SCHEMA workspace.r5_drybuild2 TO `804a3ed5-0f8d-494c-99e5-93f4c75fc644`;
GRANT SELECT ON SCHEMA workspace.r5_drybuild2 TO `804a3ed5-0f8d-494c-99e5-93f4c75fc644`;
