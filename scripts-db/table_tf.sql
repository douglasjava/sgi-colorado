-- Drop table if it already exists
DROP TABLE IF EXISTS public.trombetas_festas;

-- Create the visitors table
CREATE TABLE public.trombetas_festas (
    id SERIAL PRIMARY KEY,                   -- ID único para cada visitante
    visitor_name VARCHAR(100) NOT NULL,      -- Nome do visitante
    phone VARCHAR(20) NOT NULL,              -- Telefone do visitante
    responsible VARCHAR(100) NOT NULL,       -- Responsável (quem convidou)
    event_date DATE NOT NULL                 -- Data do evento
);