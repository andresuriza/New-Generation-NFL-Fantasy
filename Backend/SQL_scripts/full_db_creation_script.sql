--
-- PostgreSQL database dump
--

-- Dumped from database version 17.6 (Debian 17.6-0+deb13u1)
-- Dumped by pg_dump version 18.1

-- Started on 2025-11-25 10:08:45 CST

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

DROP DATABASE "XNFL-Fantasy-test";
--
-- TOC entry 3762 (class 1262 OID 26188)
-- Name: XNFL-Fantasy-test; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE "XNFL-Fantasy-test" WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'C.UTF-8';


ALTER DATABASE "XNFL-Fantasy-test" OWNER TO postgres;

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 2 (class 3079 OID 26189)
-- Name: citext; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS citext WITH SCHEMA public;


--
-- TOC entry 3763 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION citext; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION citext IS 'data type for case-insensitive character strings';


--
-- TOC entry 3 (class 3079 OID 26294)
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- TOC entry 3764 (class 0 OID 0)
-- Dependencies: 3
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- TOC entry 4 (class 3079 OID 26331)
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- TOC entry 3765 (class 0 OID 0)
-- Dependencies: 4
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- TOC entry 1013 (class 1247 OID 26601)
-- Name: designacion_lesion; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.designacion_lesion AS ENUM (
    'Healthy',
    'Questionable',
    'Doubtful',
    'Out',
    'Injured_Reserve',
    'Physically_Unable_to_Perform',
    'Did_Not_Participate',
    'D',
    'Q',
    'P',
    'FP',
    'IR',
    'PUP',
    'SUS',
    'O'
);


ALTER TYPE public.designacion_lesion OWNER TO postgres;

--
-- TOC entry 959 (class 1247 OID 26343)
-- Name: estado_liga; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.estado_liga AS ENUM (
    'Pre_draft',
    'Draft'
);


ALTER TYPE public.estado_liga OWNER TO postgres;

--
-- TOC entry 962 (class 1247 OID 26348)
-- Name: estado_usuario; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.estado_usuario AS ENUM (
    'activa',
    'bloqueado',
    'eliminada'
);


ALTER TYPE public.estado_usuario OWNER TO postgres;

--
-- TOC entry 965 (class 1247 OID 26356)
-- Name: estadousuarioenum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.estadousuarioenum AS ENUM (
    'activa',
    'bloqueado',
    'eliminada'
);


ALTER TYPE public.estadousuarioenum OWNER TO postgres;

--
-- TOC entry 968 (class 1247 OID 26364)
-- Name: posicion_jugador; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.posicion_jugador AS ENUM (
    'QB',
    'RB',
    'WR',
    'TE',
    'K',
    'DEF',
    'IR'
);


ALTER TYPE public.posicion_jugador OWNER TO postgres;

--
-- TOC entry 971 (class 1247 OID 26380)
-- Name: rol_membresia; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.rol_membresia AS ENUM (
    'Comisionado',
    'Manager'
);


ALTER TYPE public.rol_membresia OWNER TO postgres;

--
-- TOC entry 974 (class 1247 OID 26386)
-- Name: rol_usuario; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.rol_usuario AS ENUM (
    'manager',
    'administrador'
);


ALTER TYPE public.rol_usuario OWNER TO postgres;

--
-- TOC entry 977 (class 1247 OID 26392)
-- Name: rolusuarioenum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.rolusuarioenum AS ENUM (
    'manager',
    'administrador'
);


ALTER TYPE public.rolusuarioenum OWNER TO postgres;

--
-- TOC entry 263 (class 1255 OID 26397)
-- Name: audit_equipos_fantasy_changes(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.audit_equipos_fantasy_changes() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Handle INSERT
    IF TG_OP = 'INSERT' THEN
        INSERT INTO equipos_fantasy_audit (
            equipo_fantasy_id, usuario_id, accion, campo_modificado, 
            valor_anterior, valor_nuevo, timestamp_accion
        ) VALUES (
            NEW.id, NEW.usuario_id, 'CREATE', NULL, 
            NULL, NULL, NOW()
        );
        RETURN NEW;
    END IF;
    
    -- Handle UPDATE
    IF TG_OP = 'UPDATE' THEN
        -- Track name changes
        IF OLD.nombre IS DISTINCT FROM NEW.nombre THEN
            INSERT INTO equipos_fantasy_audit (
                equipo_fantasy_id, usuario_id, accion, campo_modificado, 
                valor_anterior, valor_nuevo, timestamp_accion
            ) VALUES (
                NEW.id, NEW.usuario_id, 'UPDATE_NOMBRE', 'nombre', 
                OLD.nombre, NEW.nombre, NOW()
            );
        END IF;
        
        -- Track image changes
        IF OLD.imagen_url IS DISTINCT FROM NEW.imagen_url THEN
            INSERT INTO equipos_fantasy_audit (
                equipo_fantasy_id, usuario_id, accion, campo_modificado, 
                valor_anterior, valor_nuevo, timestamp_accion
            ) VALUES (
                NEW.id, NEW.usuario_id, 'UPDATE_IMAGEN', 'imagen_url', 
                OLD.imagen_url, NEW.imagen_url, NOW()
            );
        END IF;
        
        RETURN NEW;
    END IF;
    
    -- Handle DELETE
    IF TG_OP = 'DELETE' THEN
        INSERT INTO equipos_fantasy_audit (
            equipo_fantasy_id, usuario_id, accion, campo_modificado, 
            valor_anterior, valor_nuevo, timestamp_accion
        ) VALUES (
            OLD.id, OLD.usuario_id, 'DELETE', NULL, 
            NULL, NULL, NOW()
        );
        RETURN OLD;
    END IF;
    
    RETURN NULL;
END;
$$;


ALTER FUNCTION public.audit_equipos_fantasy_changes() OWNER TO postgres;

--
-- TOC entry 320 (class 1255 OID 26632)
-- Name: audit_noticias_jugadores_changes(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.audit_noticias_jugadores_changes() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
            DECLARE
                v_usuario_id UUID;
            BEGIN
                IF TG_OP = 'DELETE' THEN
                    -- For DELETE, use OLD record data and insert audit before deletion
                    v_usuario_id := COALESCE(OLD.creado_por, (SELECT id FROM usuarios WHERE rol = 'administrador' LIMIT 1));
                    INSERT INTO noticias_jugadores_audit (noticia_id, usuario_id, accion, campo_modificado, valor_anterior)
                    VALUES (OLD.id, v_usuario_id, 'DELETE', 'all', 'Player news deleted');
                    RETURN OLD;
                ELSIF TG_OP = 'INSERT' THEN
                    -- Get the user who made the change
                    v_usuario_id := COALESCE(NEW.creado_por, (SELECT id FROM usuarios WHERE rol = 'administrador' LIMIT 1));
                    INSERT INTO noticias_jugadores_audit (noticia_id, usuario_id, accion, campo_modificado, valor_nuevo)
                    VALUES (NEW.id, v_usuario_id, 'INSERT', 'all', 'New player news created');
                    RETURN NEW;
                ELSIF TG_OP = 'UPDATE' THEN
                    -- Get the user who made the change
                    v_usuario_id := COALESCE(NEW.creado_por, (SELECT id FROM usuarios WHERE rol = 'administrador' LIMIT 1));
                    
                    -- Log changes to specific fields
                    IF OLD.texto <> NEW.texto THEN
                        INSERT INTO noticias_jugadores_audit (noticia_id, usuario_id, accion, campo_modificado, valor_anterior, valor_nuevo)
                        VALUES (NEW.id, v_usuario_id, 'UPDATE', 'texto', OLD.texto, NEW.texto);
                    END IF;
                    IF OLD.es_lesion <> NEW.es_lesion THEN
                        INSERT INTO noticias_jugadores_audit (noticia_id, usuario_id, accion, campo_modificado, valor_anterior, valor_nuevo)
                        VALUES (NEW.id, v_usuario_id, 'UPDATE', 'es_lesion', OLD.es_lesion::text, NEW.es_lesion::text);
                    END IF;
                    IF OLD.resumen IS DISTINCT FROM NEW.resumen THEN
                        INSERT INTO noticias_jugadores_audit (noticia_id, usuario_id, accion, campo_modificado, valor_anterior, valor_nuevo)
                        VALUES (NEW.id, v_usuario_id, 'UPDATE', 'resumen', OLD.resumen, NEW.resumen);
                    END IF;
                    IF OLD.designacion IS DISTINCT FROM NEW.designacion THEN
                        INSERT INTO noticias_jugadores_audit (noticia_id, usuario_id, accion, campo_modificado, valor_anterior, valor_nuevo)
                        VALUES (NEW.id, v_usuario_id, 'UPDATE', 'designacion', OLD.designacion::text, NEW.designacion::text);
                    END IF;
                    RETURN NEW;
                END IF;
                RETURN NULL;
            END;
            $$;


ALTER FUNCTION public.audit_noticias_jugadores_changes() OWNER TO postgres;

--
-- TOC entry 285 (class 1255 OID 26398)
-- Name: trg_liga_insert_add_commissioner(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.trg_liga_insert_add_commissioner() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
  v_alias TEXT;
BEGIN
  -- Tomamos el alias del usuario (o “Comisionado” si no hay)
  SELECT u.alias INTO v_alias
  FROM usuarios u
  WHERE u.id = NEW.comisionado_id;

  v_alias := COALESCE(NULLIF(v_alias, ''), 'Comisionado');

  -- Inserta membresía del comisionado (rol fijo) 
  -- Nota: no debería haber conflicto al crear la liga; ON CONFLICT por seguridad
  INSERT INTO ligas_miembros (liga_id, usuario_id, alias, rol)
  VALUES (NEW.id, NEW.comisionado_id, v_alias, 'Comisionado')
  ON CONFLICT DO NOTHING;

  -- Auditoría de incorporación
  INSERT INTO ligas_miembros_aud (liga_id, usuario_id, accion)
  VALUES (NEW.id, NEW.comisionado_id, 'unirse');

  RETURN NEW;
END;
$$;


ALTER FUNCTION public.trg_liga_insert_add_commissioner() OWNER TO postgres;

--
-- TOC entry 323 (class 1255 OID 26399)
-- Name: trg_set_actualizado_liga(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.trg_set_actualizado_liga() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  NEW.actualizado_en := now();
  RETURN NEW;
END$$;


ALTER FUNCTION public.trg_set_actualizado_liga() OWNER TO postgres;

--
-- TOC entry 251 (class 1255 OID 26400)
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.actualizado_en = NOW();
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_updated_at_column() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 220 (class 1259 OID 26401)
-- Name: equipos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.equipos (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    nombre character varying(100) NOT NULL,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    actualizado_en timestamp with time zone DEFAULT now() NOT NULL,
    thumbnail text DEFAULT 'https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.patriots.com%2Ffans%2Fdownloads-social-profile&psig=AOvVaw3P-JGFrH4UduQ4t9Kl0Rcv&ust=1760403087933000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCMjB4e76n5ADFQAAAAAdAAAAABAE'::text,
    ciudad text,
    CONSTRAINT ck_nombre_len CHECK (((length((nombre)::text) >= 1) AND (length((nombre)::text) <= 100)))
);


ALTER TABLE public.equipos OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 26411)
-- Name: equipos_fantasy; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.equipos_fantasy (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    liga_id uuid NOT NULL,
    usuario_id uuid NOT NULL,
    nombre character varying(100) NOT NULL,
    imagen_url text,
    thumbnail_url text,
    creado_en timestamp with time zone DEFAULT now(),
    actualizado_en timestamp with time zone DEFAULT now(),
    CONSTRAINT ck_imagen_url_format CHECK (((imagen_url IS NULL) OR (imagen_url ~ '\.(jpg|jpeg|png)(\?.*)?$'::text))),
    CONSTRAINT ck_nombre_equipo_fantasy_len CHECK (((length((nombre)::text) >= 1) AND (length((nombre)::text) <= 100)))
);


ALTER TABLE public.equipos_fantasy OWNER TO postgres;

--
-- TOC entry 3766 (class 0 OID 0)
-- Dependencies: 221
-- Name: COLUMN equipos_fantasy.nombre; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.equipos_fantasy.nombre IS 'Fantasy team name (1-100 chars, unique per league)';


--
-- TOC entry 3767 (class 0 OID 0)
-- Dependencies: 221
-- Name: COLUMN equipos_fantasy.imagen_url; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.equipos_fantasy.imagen_url IS 'Team image URL (JPEG/PNG, max 5MB, 300x300-1024x1024px)';


--
-- TOC entry 3768 (class 0 OID 0)
-- Dependencies: 221
-- Name: COLUMN equipos_fantasy.thumbnail_url; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.equipos_fantasy.thumbnail_url IS 'Auto-generated thumbnail from team image';


--
-- TOC entry 222 (class 1259 OID 26421)
-- Name: equipos_fantasy_audit; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.equipos_fantasy_audit (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    equipo_fantasy_id uuid NOT NULL,
    usuario_id uuid NOT NULL,
    accion character varying(50) NOT NULL,
    campo_modificado character varying(50),
    valor_anterior text,
    valor_nuevo text,
    timestamp_accion timestamp with time zone DEFAULT now()
);


ALTER TABLE public.equipos_fantasy_audit OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 26428)
-- Name: jugadores; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.jugadores (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    nombre character varying(100) NOT NULL,
    posicion public.posicion_jugador NOT NULL,
    equipo_id uuid NOT NULL,
    imagen_url text NOT NULL,
    thumbnail_url text,
    activo boolean DEFAULT true NOT NULL,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_nombre_jugador_len CHECK (((length((nombre)::text) >= 1) AND (length((nombre)::text) <= 100)))
);


ALTER TABLE public.jugadores OWNER TO postgres;

--
-- TOC entry 3769 (class 0 OID 0)
-- Dependencies: 223
-- Name: TABLE jugadores; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.jugadores IS 'NFL players assigned to real NFL teams';


--
-- TOC entry 224 (class 1259 OID 26437)
-- Name: ligas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ligas (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    nombre character varying(100) NOT NULL,
    descripcion text,
    contrasena_hash text NOT NULL,
    equipos_max smallint NOT NULL,
    estado public.estado_liga DEFAULT 'Pre_draft'::public.estado_liga NOT NULL,
    temporada_id uuid NOT NULL,
    comisionado_id uuid NOT NULL,
    playoffs_equipos smallint DEFAULT 4 NOT NULL,
    puntajes_decimales boolean DEFAULT true NOT NULL,
    trade_deadline_activa boolean DEFAULT false NOT NULL,
    limite_cambios_temp integer,
    limite_agentes_temp integer,
    formato_posiciones jsonb DEFAULT '{"K": 1, "IR": 3, "QB": 1, "RB": 2, "TE": 1, "WR": 2, "DEF": 1, "BANCA": 6, "FLEX_RB_WR": 1}'::jsonb NOT NULL,
    puntos_config jsonb DEFAULT '{"reception_points": 1, "defense_sack_points": 1, "defense_safety_points": 2, "kicking_pat_made_points": 1, "defense_touchdown_points": 6, "passing_touchdown_points": 4, "interception_thrown_points": -2, "defense_interception_points": 2, "defense_fumble_recovered_points": 2, "points_allowed_greater_30_points": -2, "passing_yards_points_per_25_yards": 1, "rushing_yards_points_per_10_yards": 1, "points_allowed_less_equal_10_points": 5, "points_allowed_less_equal_20_points": 2, "points_allowed_less_equal_30_points": 0, "receiving_yards_points_per_10_yards": 1, "field_goal_made_0_to_50_yards_points": 3, "field_goal_made_50_plus_yards_points": 5, "team_defense_two_point_return_points": 2, "rushing_or_receiving_touchdown_points": 6}'::jsonb NOT NULL,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    actualizado_en timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_nombre_liga_len CHECK (((length((nombre)::text) >= 1) AND (length((nombre)::text) <= 100))),
    CONSTRAINT ligas_equipos_max_check CHECK ((equipos_max = ANY (ARRAY[4, 6, 8, 10, 12, 14, 16, 18, 20]))),
    CONSTRAINT ligas_playoffs_equipos_check CHECK ((playoffs_equipos = ANY (ARRAY[4, 6])))
);


ALTER TABLE public.ligas OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 26454)
-- Name: ligas_miembros; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ligas_miembros (
    liga_id uuid NOT NULL,
    usuario_id uuid NOT NULL,
    alias character varying(50) NOT NULL,
    rol public.rol_membresia DEFAULT 'Manager'::public.rol_membresia NOT NULL,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_alias_len CHECK (((length((alias)::text) >= 1) AND (length((alias)::text) <= 50)))
);


ALTER TABLE public.ligas_miembros OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 26460)
-- Name: ligas_miembros_aud; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ligas_miembros_aud (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    liga_id uuid NOT NULL,
    usuario_id uuid NOT NULL,
    accion text NOT NULL,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ligas_miembros_aud_accion_check CHECK ((accion = ANY (ARRAY['unirse'::text, 'salir'::text])))
);


ALTER TABLE public.ligas_miembros_aud OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 26468)
-- Name: media; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.media (
    equipo_id uuid NOT NULL,
    url text NOT NULL,
    generado_en timestamp with time zone DEFAULT now(),
    creado_en timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.media OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 26615)
-- Name: noticias_jugadores; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.noticias_jugadores (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    jugador_id uuid NOT NULL,
    texto text NOT NULL,
    es_lesion boolean DEFAULT false NOT NULL,
    resumen character varying(200),
    designacion public.designacion_lesion,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    creado_por uuid NOT NULL,
    CONSTRAINT ck_resumen_len CHECK (((length((resumen)::text) >= 1) AND (length((resumen)::text) <= 200))),
    CONSTRAINT ck_texto_len CHECK (((length(texto) >= 1) AND (length(texto) <= 2000)))
);


ALTER TABLE public.noticias_jugadores OWNER TO postgres;

--
-- TOC entry 3770 (class 0 OID 0)
-- Dependencies: 231
-- Name: TABLE noticias_jugadores; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.noticias_jugadores IS 'Player news and injury updates';


--
-- TOC entry 3771 (class 0 OID 0)
-- Dependencies: 231
-- Name: COLUMN noticias_jugadores.texto; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.noticias_jugadores.texto IS 'News text content (1-2000 chars)';


--
-- TOC entry 3772 (class 0 OID 0)
-- Dependencies: 231
-- Name: COLUMN noticias_jugadores.es_lesion; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.noticias_jugadores.es_lesion IS 'Whether this news item is injury-related';


--
-- TOC entry 3773 (class 0 OID 0)
-- Dependencies: 231
-- Name: COLUMN noticias_jugadores.resumen; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.noticias_jugadores.resumen IS 'Brief summary of the news (1-200 chars)';


--
-- TOC entry 3774 (class 0 OID 0)
-- Dependencies: 231
-- Name: COLUMN noticias_jugadores.designacion; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.noticias_jugadores.designacion IS 'Injury designation if applicable';


--
-- TOC entry 232 (class 1259 OID 26625)
-- Name: noticias_jugadores_audit; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.noticias_jugadores_audit (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    noticia_id uuid NOT NULL,
    usuario_id uuid NOT NULL,
    accion character varying(50) NOT NULL,
    campo_modificado character varying(50),
    valor_anterior text,
    valor_nuevo text,
    timestamp_accion timestamp with time zone DEFAULT now()
);


ALTER TABLE public.noticias_jugadores_audit OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 26475)
-- Name: temporadas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.temporadas (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    nombre character varying(100) NOT NULL,
    semanas integer NOT NULL,
    fecha_inicio date NOT NULL,
    fecha_fin date NOT NULL,
    es_actual boolean DEFAULT false NOT NULL,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_temp_rango CHECK ((fecha_fin > fecha_inicio))
);


ALTER TABLE public.temporadas OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 26482)
-- Name: temporadas_semanas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.temporadas_semanas (
    temporada_id uuid NOT NULL,
    numero integer NOT NULL,
    fecha_inicio date NOT NULL,
    fecha_fin date NOT NULL,
    CONSTRAINT ck_sem_rango CHECK ((fecha_fin > fecha_inicio))
);


ALTER TABLE public.temporadas_semanas OWNER TO postgres;

--
-- TOC entry 230 (class 1259 OID 26486)
-- Name: usuarios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuarios (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    nombre character varying(50) NOT NULL,
    alias character varying(50) NOT NULL,
    correo public.citext NOT NULL,
    contrasena_hash text NOT NULL,
    rol public.rol_usuario DEFAULT 'manager'::public.rol_usuario NOT NULL,
    estado public.estado_usuario DEFAULT 'activa'::public.estado_usuario NOT NULL,
    idioma character varying(10) DEFAULT 'Ingles'::character varying NOT NULL,
    imagen_perfil_url text DEFAULT '/img/perfil/default.png'::text NOT NULL,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    failed_attempts integer DEFAULT 0,
    CONSTRAINT ck_alias_len CHECK (((length((alias)::text) >= 1) AND (length((alias)::text) <= 50))),
    CONSTRAINT ck_correo_fmt CHECK ((correo OPERATOR(public.~*) '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$'::public.citext)),
    CONSTRAINT ck_correo_len CHECK ((length((correo)::text) <= 50)),
    CONSTRAINT ck_nombre_len CHECK (((length((nombre)::text) >= 1) AND (length((nombre)::text) <= 50)))
);


ALTER TABLE public.usuarios OWNER TO postgres;

--
-- TOC entry 3555 (class 2606 OID 26503)
-- Name: equipos_fantasy_audit equipos_fantasy_audit_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipos_fantasy_audit
    ADD CONSTRAINT equipos_fantasy_audit_pkey PRIMARY KEY (id);


--
-- TOC entry 3548 (class 2606 OID 26505)
-- Name: equipos_fantasy equipos_fantasy_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipos_fantasy
    ADD CONSTRAINT equipos_fantasy_pkey PRIMARY KEY (id);


--
-- TOC entry 3560 (class 2606 OID 26507)
-- Name: jugadores jugadores_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jugadores
    ADD CONSTRAINT jugadores_pkey PRIMARY KEY (id);


--
-- TOC entry 3573 (class 2606 OID 26509)
-- Name: ligas_miembros_aud ligas_miembros_aud_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ligas_miembros_aud
    ADD CONSTRAINT ligas_miembros_aud_pkey PRIMARY KEY (id);


--
-- TOC entry 3564 (class 2606 OID 26511)
-- Name: ligas ligas_nombre_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ligas
    ADD CONSTRAINT ligas_nombre_key UNIQUE (nombre);


--
-- TOC entry 3566 (class 2606 OID 26513)
-- Name: ligas ligas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ligas
    ADD CONSTRAINT ligas_pkey PRIMARY KEY (id);


--
-- TOC entry 3575 (class 2606 OID 26515)
-- Name: media media_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.media
    ADD CONSTRAINT media_pkey PRIMARY KEY (equipo_id);


--
-- TOC entry 3590 (class 2606 OID 26636)
-- Name: noticias_jugadores_audit noticias_jugadores_audit_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.noticias_jugadores_audit
    ADD CONSTRAINT noticias_jugadores_audit_pkey PRIMARY KEY (id);


--
-- TOC entry 3588 (class 2606 OID 26634)
-- Name: noticias_jugadores noticias_jugadores_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.noticias_jugadores
    ADD CONSTRAINT noticias_jugadores_pkey PRIMARY KEY (id);


--
-- TOC entry 3568 (class 2606 OID 26517)
-- Name: ligas_miembros pk_liga_miembro; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ligas_miembros
    ADD CONSTRAINT pk_liga_miembro PRIMARY KEY (liga_id, usuario_id);


--
-- TOC entry 3582 (class 2606 OID 26519)
-- Name: temporadas_semanas pk_temp_sem; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.temporadas_semanas
    ADD CONSTRAINT pk_temp_sem PRIMARY KEY (temporada_id, numero);


--
-- TOC entry 3577 (class 2606 OID 26521)
-- Name: temporadas temporadas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.temporadas
    ADD CONSTRAINT temporadas_pkey PRIMARY KEY (id);


--
-- TOC entry 3570 (class 2606 OID 26523)
-- Name: ligas_miembros uq_alias_por_liga; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ligas_miembros
    ADD CONSTRAINT uq_alias_por_liga UNIQUE (liga_id, alias);


--
-- TOC entry 3562 (class 2606 OID 26525)
-- Name: jugadores uq_jugador_por_equipo; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jugadores
    ADD CONSTRAINT uq_jugador_por_equipo UNIQUE (equipo_id, nombre);


--
-- TOC entry 3553 (class 2606 OID 26527)
-- Name: equipos_fantasy uq_nombre_equipo_fantasy_por_liga; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipos_fantasy
    ADD CONSTRAINT uq_nombre_equipo_fantasy_por_liga UNIQUE (liga_id, nombre);


--
-- TOC entry 3580 (class 2606 OID 26529)
-- Name: temporadas uq_temporadas_nombre; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.temporadas
    ADD CONSTRAINT uq_temporadas_nombre UNIQUE (nombre);


--
-- TOC entry 3584 (class 2606 OID 26531)
-- Name: usuarios usuarios_correo_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_correo_key UNIQUE (correo);


--
-- TOC entry 3586 (class 2606 OID 26533)
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id);


--
-- TOC entry 3556 (class 1259 OID 26534)
-- Name: idx_equipos_fantasy_audit_equipo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_equipos_fantasy_audit_equipo ON public.equipos_fantasy_audit USING btree (equipo_fantasy_id);


--
-- TOC entry 3557 (class 1259 OID 26535)
-- Name: idx_equipos_fantasy_audit_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_equipos_fantasy_audit_timestamp ON public.equipos_fantasy_audit USING btree (timestamp_accion);


--
-- TOC entry 3558 (class 1259 OID 26536)
-- Name: idx_equipos_fantasy_audit_usuario; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_equipos_fantasy_audit_usuario ON public.equipos_fantasy_audit USING btree (usuario_id);


--
-- TOC entry 3549 (class 1259 OID 26537)
-- Name: idx_equipos_fantasy_liga; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_equipos_fantasy_liga ON public.equipos_fantasy USING btree (liga_id);


--
-- TOC entry 3550 (class 1259 OID 26538)
-- Name: idx_equipos_fantasy_nombre; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_equipos_fantasy_nombre ON public.equipos_fantasy USING btree (nombre);


--
-- TOC entry 3551 (class 1259 OID 26539)
-- Name: idx_equipos_fantasy_usuario; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_equipos_fantasy_usuario ON public.equipos_fantasy USING btree (usuario_id);


--
-- TOC entry 3578 (class 1259 OID 26540)
-- Name: uq_temporada_actual; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX uq_temporada_actual ON public.temporadas USING btree (es_actual) WHERE (es_actual = true);


--
-- TOC entry 3571 (class 1259 OID 26541)
-- Name: uq_unico_comisionado_por_liga; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX uq_unico_comisionado_por_liga ON public.ligas_miembros USING btree (liga_id) WHERE (rol = 'Comisionado'::public.rol_membresia);


--
-- TOC entry 3608 (class 2620 OID 26542)
-- Name: ligas trg_ligas_actualizado; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_ligas_actualizado BEFORE UPDATE ON public.ligas FOR EACH ROW EXECUTE FUNCTION public.trg_set_actualizado_liga();


--
-- TOC entry 3606 (class 2620 OID 26543)
-- Name: equipos_fantasy trigger_audit_equipos_fantasy; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trigger_audit_equipos_fantasy AFTER INSERT OR DELETE OR UPDATE ON public.equipos_fantasy FOR EACH ROW EXECUTE FUNCTION public.audit_equipos_fantasy_changes();


--
-- TOC entry 3609 (class 2620 OID 26673)
-- Name: noticias_jugadores trigger_audit_noticias_jugadores; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trigger_audit_noticias_jugadores BEFORE DELETE ON public.noticias_jugadores FOR EACH ROW EXECUTE FUNCTION public.audit_noticias_jugadores_changes();


--
-- TOC entry 3610 (class 2620 OID 26674)
-- Name: noticias_jugadores trigger_audit_noticias_jugadores_after; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trigger_audit_noticias_jugadores_after AFTER INSERT OR UPDATE ON public.noticias_jugadores FOR EACH ROW EXECUTE FUNCTION public.audit_noticias_jugadores_changes();


--
-- TOC entry 3607 (class 2620 OID 26544)
-- Name: equipos_fantasy update_equipos_fantasy_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_equipos_fantasy_updated_at BEFORE UPDATE ON public.equipos_fantasy FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 3611 (class 2620 OID 26638)
-- Name: noticias_jugadores update_noticias_jugadores_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_noticias_jugadores_updated_at BEFORE UPDATE ON public.noticias_jugadores FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 3593 (class 2606 OID 26545)
-- Name: equipos_fantasy_audit equipos_fantasy_audit_equipo_fantasy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipos_fantasy_audit
    ADD CONSTRAINT equipos_fantasy_audit_equipo_fantasy_id_fkey FOREIGN KEY (equipo_fantasy_id) REFERENCES public.equipos_fantasy(id) ON DELETE CASCADE;


--
-- TOC entry 3594 (class 2606 OID 26550)
-- Name: equipos_fantasy_audit equipos_fantasy_audit_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipos_fantasy_audit
    ADD CONSTRAINT equipos_fantasy_audit_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id) ON DELETE RESTRICT;


--
-- TOC entry 3591 (class 2606 OID 26555)
-- Name: equipos_fantasy equipos_fantasy_liga_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipos_fantasy
    ADD CONSTRAINT equipos_fantasy_liga_id_fkey FOREIGN KEY (liga_id) REFERENCES public.ligas(id) ON DELETE CASCADE;


--
-- TOC entry 3592 (class 2606 OID 26560)
-- Name: equipos_fantasy equipos_fantasy_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipos_fantasy
    ADD CONSTRAINT equipos_fantasy_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id) ON DELETE RESTRICT;


--
-- TOC entry 3595 (class 2606 OID 26565)
-- Name: ligas ligas_comisionado_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ligas
    ADD CONSTRAINT ligas_comisionado_id_fkey FOREIGN KEY (comisionado_id) REFERENCES public.usuarios(id) ON DELETE RESTRICT;


--
-- TOC entry 3599 (class 2606 OID 26570)
-- Name: ligas_miembros_aud ligas_miembros_aud_liga_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ligas_miembros_aud
    ADD CONSTRAINT ligas_miembros_aud_liga_id_fkey FOREIGN KEY (liga_id) REFERENCES public.ligas(id) ON DELETE CASCADE;


--
-- TOC entry 3600 (class 2606 OID 26575)
-- Name: ligas_miembros_aud ligas_miembros_aud_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ligas_miembros_aud
    ADD CONSTRAINT ligas_miembros_aud_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id) ON DELETE CASCADE;


--
-- TOC entry 3597 (class 2606 OID 26580)
-- Name: ligas_miembros ligas_miembros_liga_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ligas_miembros
    ADD CONSTRAINT ligas_miembros_liga_id_fkey FOREIGN KEY (liga_id) REFERENCES public.ligas(id) ON DELETE CASCADE;


--
-- TOC entry 3598 (class 2606 OID 26585)
-- Name: ligas_miembros ligas_miembros_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ligas_miembros
    ADD CONSTRAINT ligas_miembros_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id) ON DELETE CASCADE;


--
-- TOC entry 3596 (class 2606 OID 26590)
-- Name: ligas ligas_temporada_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ligas
    ADD CONSTRAINT ligas_temporada_id_fkey FOREIGN KEY (temporada_id) REFERENCES public.temporadas(id) ON DELETE RESTRICT;


--
-- TOC entry 3604 (class 2606 OID 26649)
-- Name: noticias_jugadores_audit noticias_jugadores_audit_noticia_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.noticias_jugadores_audit
    ADD CONSTRAINT noticias_jugadores_audit_noticia_id_fkey FOREIGN KEY (noticia_id) REFERENCES public.noticias_jugadores(id) ON DELETE CASCADE;


--
-- TOC entry 3605 (class 2606 OID 26654)
-- Name: noticias_jugadores_audit noticias_jugadores_audit_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.noticias_jugadores_audit
    ADD CONSTRAINT noticias_jugadores_audit_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id) ON DELETE RESTRICT;


--
-- TOC entry 3602 (class 2606 OID 26639)
-- Name: noticias_jugadores noticias_jugadores_creado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.noticias_jugadores
    ADD CONSTRAINT noticias_jugadores_creado_por_fkey FOREIGN KEY (creado_por) REFERENCES public.usuarios(id) ON DELETE RESTRICT;


--
-- TOC entry 3603 (class 2606 OID 26644)
-- Name: noticias_jugadores noticias_jugadores_jugador_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.noticias_jugadores
    ADD CONSTRAINT noticias_jugadores_jugador_id_fkey FOREIGN KEY (jugador_id) REFERENCES public.jugadores(id) ON DELETE CASCADE;


--
-- TOC entry 3601 (class 2606 OID 26595)
-- Name: temporadas_semanas temporadas_semanas_temporada_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.temporadas_semanas
    ADD CONSTRAINT temporadas_semanas_temporada_id_fkey FOREIGN KEY (temporada_id) REFERENCES public.temporadas(id) ON DELETE CASCADE;


-- Completed on 2025-11-25 10:08:45 CST

--
-- PostgreSQL database dump complete
--

