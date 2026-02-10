-- База знаний (Knowledge Base)
-- Иерархия: Situation (1) -> (N) Cause (1) -> (N) Advice
-- Ситуация -> Причины -> Рекомендации
-- All tables use standard "id" UUID PK to match project convention

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Таблица Situation (ситуации) — родитель для Cause
CREATE TABLE IF NOT EXISTS situation (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    controlled_param VARCHAR(100),
    min_value        DOUBLE PRECISION,
    max_value        DOUBLE PRECISION,
    description      VARCHAR(100)
);

COMMENT ON TABLE situation IS 'Ситуации (родительская таблица для cause)';
COMMENT ON COLUMN situation.id IS 'Идентификатор ситуации';
COMMENT ON COLUMN situation.controlled_param IS 'Контролируемый параметр';
COMMENT ON COLUMN situation.min_value IS 'Минимальное значение диапазона';
COMMENT ON COLUMN situation.max_value IS 'Максимальное значение диапазона';
COMMENT ON COLUMN situation.description IS 'Описание';

-- Таблица Cause (причины) — родитель для Advice, дочерняя для Situation
CREATE TABLE IF NOT EXISTS cause (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    situation_id UUID REFERENCES situation(id) ON DELETE CASCADE,
    description  VARCHAR(100)
);

COMMENT ON TABLE cause IS 'Причины (родитель для advice, дочерняя для situation)';
COMMENT ON COLUMN cause.id IS 'Идентификатор причины';
COMMENT ON COLUMN cause.situation_id IS 'Ссылка на ситуацию';
COMMENT ON COLUMN cause.description IS 'Описание причины';

-- Таблица Advice (рекомендации) — дочерняя для Cause
CREATE TABLE IF NOT EXISTS advice (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cause_id    UUID REFERENCES cause(id) ON DELETE CASCADE,
    description VARCHAR(50)
);

COMMENT ON TABLE advice IS 'Рекомендации (дочерняя таблица для cause)';
COMMENT ON COLUMN advice.id IS 'Идентификатор рекомендации';
COMMENT ON COLUMN advice.cause_id IS 'Ссылка на причину';
COMMENT ON COLUMN advice.description IS 'Текст рекомендации';

-- Индексы для внешних ключей
CREATE INDEX IF NOT EXISTS idx_cause_situation_id ON cause(situation_id);
CREATE INDEX IF NOT EXISTS idx_advice_cause_id ON advice(cause_id);
