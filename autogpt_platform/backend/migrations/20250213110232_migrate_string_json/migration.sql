CREATE OR REPLACE FUNCTION migrate_text_column_to_json(
    p_table         text,                       -- Table name, e.g. 'AgentNodeExecution'
    p_col           text,                       -- Column name to convert, e.g. 'executionData'
    p_default       json DEFAULT '{}'::json,    -- Fallback value when original value is NULL.
                                                -- Pass NULL here if you prefer to leave NULLs.
    p_set_nullable  boolean DEFAULT true        -- If false, the new column will be NOT NULL.
) RETURNS void AS $$
DECLARE
    full_table text;
    tmp_col    text;
BEGIN
    -- Build a fully qualified table name using the current schema.
    full_table := format('%I.%I', current_schema(), p_table);
    tmp_col := p_col || '_tmp';

    -- 0. Skip the migration if the column is already of type jsonb.
    IF EXISTS (
      SELECT 1
      FROM information_schema.columns
      WHERE table_schema = current_schema()
        AND table_name = p_table
        AND column_name = p_col
        AND data_type = 'jsonb'
    ) THEN
      RAISE NOTICE 'Column %I.%I is already of type jsonb, skipping migration.', full_table, p_col;
      RETURN;
    END IF;

    -- 1. Cleanup the original column from invalid JSON characters.
    EXECUTE format('UPDATE %s SET %I = replace(%I, E''\\u0000'', '''') WHERE %I LIKE ''%%\\u0000%%'';', full_table, p_col, p_col, p_col);

    -- 2. Add the temporary column of type JSON.
    EXECUTE format('ALTER TABLE %s ADD COLUMN %I jsonb;', full_table, tmp_col);

    -- 3. Convert the data:
    --    - If p_default IS NOT NULL, use it as the fallback value.
    --    - Otherwise, keep NULL.
    IF p_default IS NULL THEN
      EXECUTE format(
        'UPDATE %s SET %I = CASE WHEN %I IS NULL THEN NULL ELSE %I::json END;',
         full_table, tmp_col, p_col, p_col
      );
    ELSE
      EXECUTE format(
        'UPDATE %s SET %I = CASE WHEN %I IS NULL THEN %L::json ELSE %I::json END;',
         full_table, tmp_col, p_col, p_default::text, p_col
      );
    END IF;

    -- 4. Drop the original text column.
    EXECUTE format('ALTER TABLE %s DROP COLUMN %I;', full_table, p_col);

    -- 5. Rename the temporary column to the original column name.
    EXECUTE format('ALTER TABLE %s RENAME COLUMN %I TO %I;', full_table, tmp_col, p_col);

    -- 6. Optionally set a DEFAULT for future inserts if a fallback is provided.
    IF p_default IS NOT NULL THEN
      EXECUTE format('ALTER TABLE %s ALTER COLUMN %I SET DEFAULT %L::json;',
                     full_table, p_col, p_default::text);
    END IF;

    -- 7. Optionally mark the column as NOT NULL.
    IF NOT p_set_nullable THEN
      EXECUTE format('ALTER TABLE %s ALTER COLUMN %I SET NOT NULL;', full_table, p_col);
    END IF;
END;
$$ LANGUAGE plpgsql;


BEGIN;
  SELECT migrate_text_column_to_json('AgentGraphExecution', 'stats', NULL, true);
  SELECT migrate_text_column_to_json('AgentNodeExecution', 'stats', NULL, true);
  SELECT migrate_text_column_to_json('AgentNodeExecution', 'executionData', NULL, true);
  SELECT migrate_text_column_to_json('AgentNode', 'constantInput', '{}'::json, false);
  SELECT migrate_text_column_to_json('AgentNode', 'metadata', '{}'::json, false);
  SELECT migrate_text_column_to_json('AgentNodeExecutionInputOutput', 'data', NULL, false);
COMMIT;
