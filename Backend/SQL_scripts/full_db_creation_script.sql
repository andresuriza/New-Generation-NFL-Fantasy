--
-- PostgreSQL database dump
--

\restrict vWBpLli6Raw0bKVaLvMEdh9iNM4ycEAv9FbHFlpRFU7immuRYNGG4gZZDh5nUZJ

-- Dumped from database version 17.6 (Debian 17.6-0+deb13u1)
-- Dumped by pg_dump version 18.0

-- Started on 2025-11-08 12:43:38 CST

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
-- TOC entry 3743 (class 1262 OID 16623)
-- Name: XNFL-Fantasy; Type: DATABASE; Schema: -; Owner: -
--

CREATE DATABASE "XNFL-Fantasy" WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'C.UTF-8';


\unrestrict vWBpLli6Raw0bKVaLvMEdh9iNM4ycEAv9FbHFlpRFU7immuRYNGG4gZZDh5nUZJ
\encoding SQL_ASCII
\connect -reuse-previous=on "dbname='XNFL-Fantasy'"
\restrict vWBpLli6Raw0bKVaLvMEdh9iNM4ycEAv9FbHFlpRFU7immuRYNGG4gZZDh5nUZJ

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
-- TOC entry 7 (class 2615 OID 2200)
-- Name: public; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA public;


--
-- TOC entry 3744 (class 0 OID 0)
-- Dependencies: 7
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON SCHEMA public IS 'standard public schema';


--
-- TOC entry 980 (class 1247 OID 17317)
-- Name: estado_liga; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.estado_liga AS ENUM (
    'Pre_draft',
    'Draft'
);


--
-- TOC entry 957 (class 1247 OID 16900)
-- Name: estado_usuario; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.estado_usuario AS ENUM (
    'activa',
    'bloqueado',
    'eliminada'
);


--
-- TOC entry 974 (class 1247 OID 17112)
-- Name: estadousuarioenum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.estadousuarioenum AS ENUM (
    'activa',
    'bloqueado',
    'eliminada'
);


--
-- TOC entry 998 (class 1247 OID 25545)
-- Name: posicion_jugador; Type: TYPE; Schema: public; Owner: -
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


--
-- TOC entry 989 (class 1247 OID 17399)
-- Name: rol_membresia; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.rol_membresia AS ENUM (
    'Comisionado',
    'Manager'
);


--
-- TOC entry 954 (class 1247 OID 16895)
-- Name: rol_usuario; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.rol_usuario AS ENUM (
    'manager',
    'administrador'
);


--
-- TOC entry 971 (class 1247 OID 17107)
-- Name: rolusuarioenum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.rolusuarioenum AS ENUM (
    'manager',
    'administrador'
);


--
-- TOC entry 244 (class 1255 OID 25645)
-- Name: audit_equipos_fantasy_changes(); Type: FUNCTION; Schema: public; Owner: -
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


--
-- TOC entry 312 (class 1255 OID 17457)
-- Name: trg_liga_insert_add_commissioner(); Type: FUNCTION; Schema: public; Owner: -
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


--
-- TOC entry 254 (class 1255 OID 17352)
-- Name: trg_set_actualizado_liga(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.trg_set_actualizado_liga() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  NEW.actualizado_en := now();
  RETURN NEW;
END$$;


--
-- TOC entry 232 (class 1255 OID 25643)
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.actualizado_en = NOW();
    RETURN NEW;
END;
$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 221 (class 1259 OID 17068)
-- Name: equipos; Type: TABLE; Schema: public; Owner: -
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


--
-- TOC entry 229 (class 1259 OID 25594)
-- Name: equipos_fantasy; Type: TABLE; Schema: public; Owner: -
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


--
-- TOC entry 3745 (class 0 OID 0)
-- Dependencies: 229
-- Name: COLUMN equipos_fantasy.nombre; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.equipos_fantasy.nombre IS 'Fantasy team name (1-100 chars, unique per league)';


--
-- TOC entry 3746 (class 0 OID 0)
-- Dependencies: 229
-- Name: COLUMN equipos_fantasy.imagen_url; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.equipos_fantasy.imagen_url IS 'Team image URL (JPEG/PNG, max 5MB, 300x300-1024x1024px)';


--
-- TOC entry 3747 (class 0 OID 0)
-- Dependencies: 229
-- Name: COLUMN equipos_fantasy.thumbnail_url; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.equipos_fantasy.thumbnail_url IS 'Auto-generated thumbnail from team image';


--
-- TOC entry 230 (class 1259 OID 25618)
-- Name: equipos_fantasy_audit; Type: TABLE; Schema: public; Owner: -
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


--
-- TOC entry 228 (class 1259 OID 25559)
-- Name: jugadores; Type: TABLE; Schema: public; Owner: -
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


--
-- TOC entry 3748 (class 0 OID 0)
-- Dependencies: 228
-- Name: TABLE jugadores; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.jugadores IS 'NFL players assigned to real NFL teams';


--
-- TOC entry 224 (class 1259 OID 17354)
-- Name: ligas; Type: TABLE; Schema: public; Owner: -
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


--
-- TOC entry 226 (class 1259 OID 17403)
-- Name: ligas_miembros; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ligas_miembros (
    liga_id uuid NOT NULL,
    usuario_id uuid NOT NULL,
    alias character varying(50) NOT NULL,
    rol public.rol_membresia DEFAULT 'Manager'::public.rol_membresia NOT NULL,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_alias_len CHECK (((length((alias)::text) >= 1) AND (length((alias)::text) <= 50)))
);


--
-- TOC entry 227 (class 1259 OID 17424)
-- Name: ligas_miembros_aud; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ligas_miembros_aud (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    liga_id uuid NOT NULL,
    usuario_id uuid NOT NULL,
    accion text NOT NULL,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ligas_miembros_aud_accion_check CHECK ((accion = ANY (ARRAY['unirse'::text, 'salir'::text])))
);


--
-- TOC entry 222 (class 1259 OID 17091)
-- Name: media; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.media (
    equipo_id uuid NOT NULL,
    url text NOT NULL,
    generado_en timestamp with time zone DEFAULT now(),
    creado_en timestamp with time zone DEFAULT now() NOT NULL
);


--
-- TOC entry 223 (class 1259 OID 17304)
-- Name: temporadas; Type: TABLE; Schema: public; Owner: -
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


--
-- TOC entry 225 (class 1259 OID 17387)
-- Name: temporadas_semanas; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.temporadas_semanas (
    temporada_id uuid NOT NULL,
    numero integer NOT NULL,
    fecha_inicio date NOT NULL,
    fecha_fin date NOT NULL,
    CONSTRAINT ck_sem_rango CHECK ((fecha_fin > fecha_inicio))
);


--
-- TOC entry 220 (class 1259 OID 17049)
-- Name: usuarios; Type: TABLE; Schema: public; Owner: -
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


--
-- TOC entry 3728 (class 0 OID 17068)
-- Dependencies: 221
-- Data for Name: equipos; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.equipos VALUES ('849db40e-753c-4566-98d5-450e202be269', 'equipo2', '2025-10-12 20:01:00.126957-06', '2025-10-12 20:38:40.961521-06', 'https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.patriots.com%2Ffans%2Fdownloads-social-profile&psig=AOvVaw3P-JGFrH4UduQ4t9Kl0Rcv&ust=1760403087933000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCMjB4e76n5ADFQAAAAAdAAAAABAE', 'cartago');
INSERT INTO public.equipos VALUES ('e8a9d8f3-bf08-4dac-950a-fc436618feda', 'Equipo Test', '2025-10-12 20:44:57.022044-06', '2025-10-12 20:44:57.052607-06', '/media/equipos/e8a9d8f3-bf08-4dac-950a-fc436618feda/New_England_Patriots_logo.png', 'cartago');
INSERT INTO public.equipos VALUES ('9ca088f0-0c5e-4c4d-a543-f626ddc4c868', 'equipo123', '2025-10-12 19:39:52.735408-06', '2025-10-12 21:03:11.543221-06', 'https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.patriots.com%2Ffans%2Fdownloads-social-profile&psig=AOvVaw3P-JGFrH4UduQ4t9Kl0Rcv&ust=1760403087933000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCMjB4e76n5ADFQAAAAAdAAAAABAE', 'cartago');
INSERT INTO public.equipos VALUES ('49075efd-6886-497e-903d-d6e4cac10b62', 'Equipo Uriza', '2025-10-12 21:55:18.039058-06', '2025-10-12 21:55:18.072774-06', '/media/equipos/49075efd-6886-497e-903d-d6e4cac10b62/New_England_Patriots_logo.png', 'cartago');
INSERT INTO public.equipos VALUES ('0f3ab3af-392d-4829-83ce-b89702109035', 'Equipo x', '2025-10-18 17:49:12.191821-06', '2025-10-18 17:49:12.219966-06', '/media/equipos/0f3ab3af-392d-4829-83ce-b89702109035/New_England_Patriots_logo.png', 'cartago');
INSERT INTO public.equipos VALUES ('8ea558db-db80-4853-9ddf-fb9d0dbcdcd4', 'Buffalo Bills', '2025-11-08 12:31:17.401275-06', '2025-11-08 12:31:17.401275-06', 'https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.patriots.com%2Ffans%2Fdownloads-social-profile&psig=AOvVaw3P-JGFrH4UduQ4t9Kl0Rcv&ust=1760403087933000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCMjB4e76n5ADFQAAAAAdAAAAABAE', 'Buffalo');
INSERT INTO public.equipos VALUES ('a8436428-2fa2-4c0b-b970-292a5f3f1513', 'Tennessee Titans', '2025-11-08 12:31:17.401275-06', '2025-11-08 12:31:17.401275-06', 'https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.patriots.com%2Ffans%2Fdownloads-social-profile&psig=AOvVaw3P-JGFrH4UduQ4t9Kl0Rcv&ust=1760403087933000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCMjB4e76n5ADFQAAAAAdAAAAABAE', 'Nashville');
INSERT INTO public.equipos VALUES ('8f892521-b310-4468-af96-ced9c6580fb3', 'Kansas City Chiefs', '2025-11-08 12:31:17.401275-06', '2025-11-08 12:31:17.401275-06', 'https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.patriots.com%2Ffans%2Fdownloads-social-profile&psig=AOvVaw3P-JGFrH4UduQ4t9Kl0Rcv&ust=1760403087933000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCMjB4e76n5ADFQAAAAAdAAAAABAE', 'Kansas City');
INSERT INTO public.equipos VALUES ('0d83123f-4dbc-4d12-ba06-88af4832eb06', 'Baltimore Ravens', '2025-11-08 12:31:17.401275-06', '2025-11-08 12:31:17.401275-06', 'https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.patriots.com%2Ffans%2Fdownloads-social-profile&psig=AOvVaw3P-JGFrH4UduQ4t9Kl0Rcv&ust=1760403087933000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCMjB4e76n5ADFQAAAAAdAAAAABAE', 'Baltimore');
INSERT INTO public.equipos VALUES ('be493a32-150a-4e27-8d17-cbb11d2d6b2f', 'Green Bay Packers', '2025-11-08 12:31:17.401275-06', '2025-11-08 12:31:17.401275-06', 'https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.patriots.com%2Ffans%2Fdownloads-social-profile&psig=AOvVaw3P-JGFrH4UduQ4t9Kl0Rcv&ust=1760403087933000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCMjB4e76n5ADFQAAAAAdAAAAABAE', 'Green Bay');
INSERT INTO public.equipos VALUES ('cb3b76bd-a213-472e-8c96-2dc46157e607', 'Dallas Cowboys', '2025-11-08 12:31:17.401275-06', '2025-11-08 12:31:17.401275-06', 'https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.patriots.com%2Ffans%2Fdownloads-social-profile&psig=AOvVaw3P-JGFrH4UduQ4t9Kl0Rcv&ust=1760403087933000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCMjB4e76n5ADFQAAAAAdAAAAABAE', 'Dallas');
INSERT INTO public.equipos VALUES ('99b0949c-a927-4bdc-b672-198c2bb15eeb', 'San Francisco 49ers', '2025-11-08 12:31:17.401275-06', '2025-11-08 12:31:17.401275-06', 'https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.patriots.com%2Ffans%2Fdownloads-social-profile&psig=AOvVaw3P-JGFrH4UduQ4t9Kl0Rcv&ust=1760403087933000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCMjB4e76n5ADFQAAAAAdAAAAABAE', 'San Francisco');
INSERT INTO public.equipos VALUES ('1ddb449f-959b-4f52-90aa-148392b260f8', 'New Orleans Saints', '2025-11-08 12:31:17.401275-06', '2025-11-08 12:31:17.401275-06', 'https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.patriots.com%2Ffans%2Fdownloads-social-profile&psig=AOvVaw3P-JGFrH4UduQ4t9Kl0Rcv&ust=1760403087933000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCMjB4e76n5ADFQAAAAAdAAAAABAE', 'New Orleans');
INSERT INTO public.equipos VALUES ('82fd3715-a695-4d17-81aa-8b047d6cb2e0', 'Los Angeles Rams', '2025-11-08 12:31:17.401275-06', '2025-11-08 12:31:17.401275-06', 'https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.patriots.com%2Ffans%2Fdownloads-social-profile&psig=AOvVaw3P-JGFrH4UduQ4t9Kl0Rcv&ust=1760403087933000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCMjB4e76n5ADFQAAAAAdAAAAABAE', 'Los Angeles');
INSERT INTO public.equipos VALUES ('1a543038-d810-4988-a730-702fc66cf774', 'Las Vegas Raiders', '2025-11-08 12:31:17.401275-06', '2025-11-08 12:31:17.401275-06', 'https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.patriots.com%2Ffans%2Fdownloads-social-profile&psig=AOvVaw3P-JGFrH4UduQ4t9Kl0Rcv&ust=1760403087933000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCMjB4e76n5ADFQAAAAAdAAAAABAE', 'Las Vegas');
INSERT INTO public.equipos VALUES ('089e94d3-7d97-45a5-823a-820eb874a2d3', 'Pittsburgh Steelers', '2025-11-08 12:31:17.401275-06', '2025-11-08 12:31:17.401275-06', 'https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.patriots.com%2Ffans%2Fdownloads-social-profile&psig=AOvVaw3P-JGFrH4UduQ4t9Kl0Rcv&ust=1760403087933000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCMjB4e76n5ADFQAAAAAdAAAAABAE', 'Pittsburgh');
INSERT INTO public.equipos VALUES ('50310f20-b192-4acd-a8a5-0c77fa5d3d94', 'Cleveland Browns', '2025-11-08 12:31:17.401275-06', '2025-11-08 12:31:17.401275-06', 'https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.patriots.com%2Ffans%2Fdownloads-social-profile&psig=AOvVaw3P-JGFrH4UduQ4t9Kl0Rcv&ust=1760403087933000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCMjB4e76n5ADFQAAAAAdAAAAABAE', 'Cleveland');
INSERT INTO public.equipos VALUES ('45a186c7-6407-4971-8607-2f43e1a821a2', 'Cincinnati Bengals', '2025-11-08 12:31:17.401275-06', '2025-11-08 12:31:17.401275-06', 'https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.patriots.com%2Ffans%2Fdownloads-social-profile&psig=AOvVaw3P-JGFrH4UduQ4t9Kl0Rcv&ust=1760403087933000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCMjB4e76n5ADFQAAAAAdAAAAABAE', 'Cincinnati');


--
-- TOC entry 3736 (class 0 OID 25594)
-- Dependencies: 229
-- Data for Name: equipos_fantasy; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.equipos_fantasy VALUES ('7a8a44e3-5fd1-43a3-81aa-22724126e1b6', '6d834883-b204-4e08-b80f-657ca39d3be6', 'df891b68-555b-4dca-bbbf-cb963dc25f48', 'abner2111', NULL, NULL, '2025-11-07 20:04:11.723826-06', '2025-11-07 20:04:11.723826-06');
INSERT INTO public.equipos_fantasy VALUES ('95f20db7-26e1-469e-ace4-231dd0c6aa29', '6d834883-b204-4e08-b80f-657ca39d3be6', 'f40e354d-1bf7-4b3e-9caa-fc234db264ac', 'Alias', NULL, NULL, '2025-11-07 20:05:21.004626-06', '2025-11-07 20:05:21.004626-06');


--
-- TOC entry 3737 (class 0 OID 25618)
-- Dependencies: 230
-- Data for Name: equipos_fantasy_audit; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.equipos_fantasy_audit VALUES ('26dbaa5b-4e27-4c20-8d34-301ab2424b29', '7a8a44e3-5fd1-43a3-81aa-22724126e1b6', 'df891b68-555b-4dca-bbbf-cb963dc25f48', 'CREATE', NULL, NULL, NULL, '2025-11-07 20:04:11.723826-06');
INSERT INTO public.equipos_fantasy_audit VALUES ('668cb812-855d-4018-a589-a918bcf0294e', '95f20db7-26e1-469e-ace4-231dd0c6aa29', 'f40e354d-1bf7-4b3e-9caa-fc234db264ac', 'CREATE', NULL, NULL, NULL, '2025-11-07 20:05:21.004626-06');


--
-- TOC entry 3735 (class 0 OID 25559)
-- Dependencies: 228
-- Data for Name: jugadores; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.jugadores VALUES ('ab90ae51-a90b-4c82-bf18-cb87755fc4a9', 'Patacón', 'QB', '849db40e-753c-4566-98d5-450e202be269', '/home/abner/amplificador de salida.png', NULL, true, '2025-11-08 12:18:54.856283-06');
INSERT INTO public.jugadores VALUES ('8a0f38fe-83f0-422d-a583-b219ce819952', 'Josh Allen', 'QB', '8ea558db-db80-4853-9ddf-fb9d0dbcdcd4', 'https://static.www.nfl.com/image/private/t_player_profile_landscape_2x/f_auto/league/josh-allen-headshot.jpg', 'https://static.www.nfl.com/image/private/t_player_profile_landscape_2x/f_auto/league/josh-allen-headshot_thumb.jpg', true, '2025-11-08 12:36:01.228035-06');
INSERT INTO public.jugadores VALUES ('d3f58acb-f51e-4b05-982f-fc01ac74aa6e', 'Stefon Diggs', 'WR', '8ea558db-db80-4853-9ddf-fb9d0dbcdcd4', 'https://static.www.nfl.com/image/private/t_player_profile_landscape_2x/f_auto/league/stefon-diggs-headshot.jpg', 'https://static.www.nfl.com/image/private/t_player_profile_landscape_2x/f_auto/league/stefon-diggs-headshot_thumb.jpg', true, '2025-11-08 12:36:01.228035-06');
INSERT INTO public.jugadores VALUES ('1ca903a0-770e-4dde-b635-4ca5e4709af3', 'Derrick Henry', 'RB', 'a8436428-2fa2-4c0b-b970-292a5f3f1513', 'https://static.www.nfl.com/image/private/t_player_profile_landscape_2x/f_auto/league/derrick-henry-headshot.jpg', 'https://static.www.nfl.com/image/private/t_player_profile_landscape_2x/f_auto/league/derrick-henry-headshot_thumb.jpg', true, '2025-11-08 12:36:01.228035-06');
INSERT INTO public.jugadores VALUES ('fcaff2b4-3d42-4c44-8666-ac43fb8ab95e', 'Travis Kelce', 'TE', '8f892521-b310-4468-af96-ced9c6580fb3', 'https://static.www.nfl.com/image/private/t_player_profile_landscape_2x/f_auto/league/travis-kelce-headshot.jpg', 'https://static.www.nfl.com/image/private/t_player_profile_landscape_2x/f_auto/league/travis-kelce-headshot_thumb.jpg', true, '2025-11-08 12:36:01.228035-06');
INSERT INTO public.jugadores VALUES ('f82e0915-d555-40e2-88db-71a65fa2d010', 'Patrick Mahomes', 'QB', '8f892521-b310-4468-af96-ced9c6580fb3', 'https://static.www.nfl.com/image/private/t_player_profile_landscape_2x/f_auto/league/patrick-mahomes-headshot.jpg', 'https://static.www.nfl.com/image/private/t_player_profile_landscape_2x/f_auto/league/patrick-mahomes-headshot_thumb.jpg', true, '2025-11-08 12:36:01.228035-06');
INSERT INTO public.jugadores VALUES ('538901b8-3660-4519-be76-ea7474597ece', 'Lamar Jackson', 'QB', '0d83123f-4dbc-4d12-ba06-88af4832eb06', 'https://static.www.nfl.com/image/private/t_player_profile_landscape_2x/f_auto/league/lamar-jackson-headshot.jpg', 'https://static.www.nfl.com/image/private/t_player_profile_landscape_2x/f_auto/league/lamar-jackson-headshot_thumb.jpg', true, '2025-11-08 12:36:01.228035-06');
INSERT INTO public.jugadores VALUES ('6dfc7c6d-6508-457c-8ba9-3d616bb1c7ff', 'Aaron Rodgers', 'QB', 'be493a32-150a-4e27-8d17-cbb11d2d6b2f', 'https://static.www.nfl.com/image/private/t_player_profile_landscape_2x/f_auto/league/aaron-rodgers-headshot.jpg', 'https://static.www.nfl.com/image/private/t_player_profile_landscape_2x/f_auto/league/aaron-rodgers-headshot_thumb.jpg', true, '2025-11-08 12:36:01.228035-06');
INSERT INTO public.jugadores VALUES ('752361cc-e2df-4f18-babc-1885bbc09d02', 'Dak Prescott', 'QB', 'cb3b76bd-a213-472e-8c96-2dc46157e607', 'https://static.www.nfl.com/image/private/t_player_profile_landscape_2x/f_auto/league/dak-prescott-headshot.jpg', 'https://static.www.nfl.com/image/private/t_player_profile_landscape_2x/f_auto/league/dak-prescott-headshot_thumb.jpg', true, '2025-11-08 12:36:01.228035-06');
INSERT INTO public.jugadores VALUES ('4769781a-b954-4a36-af2c-3d1f0e019292', 'Christian McCaffrey', 'RB', '99b0949c-a927-4bdc-b672-198c2bb15eeb', 'https://static.www.nfl.com/image/private/t_player_profile_landscape_2x/f_auto/league/christian-mccaffrey-headshot.jpg', 'https://static.www.nfl.com/image/private/t_player_profile_landscape_2x/f_auto/league/christian-mccaffrey-headshot_thumb.jpg', true, '2025-11-08 12:36:01.228035-06');
INSERT INTO public.jugadores VALUES ('204526db-07df-4931-a5b1-678ef762b803', 'Alvin Kamara', 'RB', '1ddb449f-959b-4f52-90aa-148392b260f8', 'https://static.www.nfl.com/image/private/t_player_profile_landscape_2x/f_auto/league/alvin-kamara-headshot.jpg', 'https://static.www.nfl.com/image/private/t_player_profile_landscape_2x/f_auto/league/alvin-kamara-headshot_thumb.jpg', true, '2025-11-08 12:36:01.228035-06');
INSERT INTO public.jugadores VALUES ('8b4fd87c-c5eb-4476-b316-fefee3db9155', 'Cooper Kupp', 'WR', '82fd3715-a695-4d17-81aa-8b047d6cb2e0', 'https://static.www.nfl.com/image/private/t_player_profile_landscape_2x/f_auto/league/cooper-kupp-headshot.jpg', 'https://static.www.nfl.com/image/private/t_player_profile_landscape_2x/f_auto/league/cooper-kupp-headshot_thumb.jpg', true, '2025-11-08 12:36:01.228035-06');
INSERT INTO public.jugadores VALUES ('eb533936-64f2-438b-8e57-db8b1cbb868c', 'Davante Adams', 'WR', '1a543038-d810-4988-a730-702fc66cf774', 'https://static.www.nfl.com/image/private/t_player_profile_landscape_2x/f_auto/league/davante-adams-headshot.jpg', 'https://static.www.nfl.com/image/private/t_player_profile_landscape_2x/f_auto/league/davante-adams-headshot_thumb.jpg', true, '2025-11-08 12:36:01.228035-06');
INSERT INTO public.jugadores VALUES ('3fdec9f9-ce9a-454c-94c3-3d9400a25df8', 'George Kittle', 'TE', '99b0949c-a927-4bdc-b672-198c2bb15eeb', 'https://static.www.nfl.com/image/private/t_player_profile_landscape_2x/f_auto/league/george-kittle-headshot.jpg', 'https://static.www.nfl.com/image/private/t_player_profile_landscape_2x/f_auto/league/george-kittle-headshot_thumb.jpg', true, '2025-11-08 12:36:01.228035-06');
INSERT INTO public.jugadores VALUES ('a18aceaa-64d3-474d-8148-2c8bfa29cd50', 'Mark Andrews', 'TE', '0d83123f-4dbc-4d12-ba06-88af4832eb06', 'https://static.www.nfl.com/image/private/t_player_profile_landscape_2x/f_auto/league/mark-andrews-headshot.jpg', 'https://static.www.nfl.com/image/private/t_player_profile_landscape_2x/f_auto/league/mark-andrews-headshot_thumb.jpg', true, '2025-11-08 12:36:01.228035-06');
INSERT INTO public.jugadores VALUES ('6115e1dd-df8f-4296-b5d5-76d9edfa4fe3', 'Justin Tucker', 'K', '0d83123f-4dbc-4d12-ba06-88af4832eb06', 'https://static.www.nfl.com/image/private/t_player_profile_landscape_2x/f_auto/league/justin-tucker-headshot.jpg', 'https://static.www.nfl.com/image/private/t_player_profile_landscape_2x/f_auto/league/justin-tucker-headshot_thumb.jpg', true, '2025-11-08 12:36:01.228035-06');
INSERT INTO public.jugadores VALUES ('0092d8f1-6979-4bd2-aa91-bb8f6d6fb0f8', 'Aaron Donald', 'DEF', '82fd3715-a695-4d17-81aa-8b047d6cb2e0', 'https://static.www.nfl.com/image/private/t_player_profile_landscape_2x/f_auto/league/aaron-donald-headshot.jpg', 'https://static.www.nfl.com/image/private/t_player_profile_landscape_2x/f_auto/league/aaron-donald-headshot_thumb.jpg', true, '2025-11-08 12:36:01.228035-06');
INSERT INTO public.jugadores VALUES ('4188e4f1-5c05-4141-a025-21d113bc5ace', 'T.J. Watt', 'DEF', '089e94d3-7d97-45a5-823a-820eb874a2d3', 'https://static.www.nfl.com/image/private/t_player_profile_landscape_2x/f_auto/league/tj-watt-headshot.jpg', 'https://static.www.nfl.com/image/private/t_player_profile_landscape_2x/f_auto/league/tj-watt-headshot_thumb.jpg', true, '2025-11-08 12:36:01.228035-06');
INSERT INTO public.jugadores VALUES ('0add8d41-69e0-428f-abdf-9e0fcc52482c', 'Nick Chubb', 'RB', '50310f20-b192-4acd-a8a5-0c77fa5d3d94', 'https://static.www.nfl.com/image/private/t_player_profile_landscape_2x/f_auto/league/nick-chubb-headshot.jpg', 'https://static.www.nfl.com/image/private/t_player_profile_landscape_2x/f_auto/league/nick-chubb-headshot_thumb.jpg', true, '2025-11-08 12:36:01.228035-06');
INSERT INTO public.jugadores VALUES ('3de20cb7-0dc0-409a-848c-04f3f92b540b', 'Joe Burrow', 'QB', '45a186c7-6407-4971-8607-2f43e1a821a2', 'https://static.www.nfl.com/image/private/t_player_profile_landscape_2x/f_auto/league/joe-burrow-headshot.jpg', 'https://static.www.nfl.com/image/private/t_player_profile_landscape_2x/f_auto/league/joe-burrow-headshot_thumb.jpg', true, '2025-11-08 12:36:01.228035-06');
INSERT INTO public.jugadores VALUES ('4705a8bd-0986-4673-a281-4f13f88d4487', 'Ja''Marr Chase', 'WR', '45a186c7-6407-4971-8607-2f43e1a821a2', 'https://static.www.nfl.com/image/private/t_player_profile_landscape_2x/f_auto/league/jamarr-chase-headshot.jpg', 'https://static.www.nfl.com/image/private/t_player_profile_landscape_2x/f_auto/league/jamarr-chase-headshot_thumb.jpg', true, '2025-11-08 12:36:01.228035-06');


--
-- TOC entry 3731 (class 0 OID 17354)
-- Dependencies: 224
-- Data for Name: ligas; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.ligas VALUES ('2eb77049-29f9-45cc-b5b9-7cfb9ced0fc7', 'string', 'string', '$2b$12$mNXkHNYmTIz4SmaTnFMcau/0HVHkWwQjsmrnfeklW29uwkzHHLgfO', 4, 'Pre_draft', 'b0ffc62f-e6da-45cf-bff9-ba260b168556', 'c956bff1-92b2-4f74-85cc-cfa0dc99e3b9', 4, true, false, 0, 0, '{"additionalProp1": 0, "additionalProp2": 0, "additionalProp3": 0}', '{}', '2025-10-22 12:44:51.555598-06', '2025-10-22 12:44:51.555598-06');
INSERT INTO public.ligas VALUES ('b5af3f63-b5b7-4632-b166-b90a8bc26081', 'Test Liga Success', NULL, '$2b$12$0pYzX4ft6.4fMm0q7mQuT.L8iRvyHXx.YnIC1DuTzRKGKMgkuoiN.', 4, 'Pre_draft', 'b0ffc62f-e6da-45cf-bff9-ba260b168556', 'c956bff1-92b2-4f74-85cc-cfa0dc99e3b9', 4, true, false, NULL, NULL, 'null', 'null', '2025-10-22 12:46:07.512595-06', '2025-10-22 12:46:07.512595-06');
INSERT INTO public.ligas VALUES ('6d834883-b204-4e08-b80f-657ca39d3be6', 'liga 1 test', '', '$2b$12$ufxhrPvm3Eu.vAA4iG3OHervMNUgZpe4MPapMjrZVNyRvt8PyhJpC', 4, 'Pre_draft', 'b0ffc62f-e6da-45cf-bff9-ba260b168556', 'df891b68-555b-4dca-bbbf-cb963dc25f48', 4, true, false, NULL, NULL, 'null', 'null', '2025-11-07 20:04:11.723826-06', '2025-11-07 20:04:11.723826-06');


--
-- TOC entry 3733 (class 0 OID 17403)
-- Dependencies: 226
-- Data for Name: ligas_miembros; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.ligas_miembros VALUES ('2eb77049-29f9-45cc-b5b9-7cfb9ced0fc7', 'c956bff1-92b2-4f74-85cc-cfa0dc99e3b9', 'abner2111', 'Comisionado', '2025-10-22 12:44:51.555598-06');
INSERT INTO public.ligas_miembros VALUES ('b5af3f63-b5b7-4632-b166-b90a8bc26081', 'c956bff1-92b2-4f74-85cc-cfa0dc99e3b9', 'abner2111', 'Comisionado', '2025-10-22 12:46:07.512595-06');
INSERT INTO public.ligas_miembros VALUES ('b5af3f63-b5b7-4632-b166-b90a8bc26081', '80477dbd-86eb-467c-976e-648d55ba0def', 'TestUser1', 'Manager', '2025-10-22 12:50:09.007501-06');
INSERT INTO public.ligas_miembros VALUES ('b5af3f63-b5b7-4632-b166-b90a8bc26081', 'dfd20583-861c-453f-a1cb-161b75e73220', 'TestUser2', 'Manager', '2025-10-22 12:50:19.393753-06');
INSERT INTO public.ligas_miembros VALUES ('b5af3f63-b5b7-4632-b166-b90a8bc26081', '18e11ec2-59e1-49f5-8567-e4db170cf115', 'TestUser3', 'Manager', '2025-10-22 12:50:27.941238-06');
INSERT INTO public.ligas_miembros VALUES ('b5af3f63-b5b7-4632-b166-b90a8bc26081', 'ad2b73ce-5c35-4541-9b02-2bdfa046ab90', 'TestUser4', 'Manager', '2025-10-22 12:53:09.063805-06');
INSERT INTO public.ligas_miembros VALUES ('6d834883-b204-4e08-b80f-657ca39d3be6', 'df891b68-555b-4dca-bbbf-cb963dc25f48', 'abner2111', 'Comisionado', '2025-11-07 20:04:11.723826-06');
INSERT INTO public.ligas_miembros VALUES ('6d834883-b204-4e08-b80f-657ca39d3be6', 'f40e354d-1bf7-4b3e-9caa-fc234db264ac', 'Alias', 'Manager', '2025-11-07 20:05:21.004626-06');


--
-- TOC entry 3734 (class 0 OID 17424)
-- Dependencies: 227
-- Data for Name: ligas_miembros_aud; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.ligas_miembros_aud VALUES ('815a32a8-ee72-4f47-af2f-9ec62ff4a67c', '2eb77049-29f9-45cc-b5b9-7cfb9ced0fc7', 'c956bff1-92b2-4f74-85cc-cfa0dc99e3b9', 'unirse', '2025-10-22 12:44:51.555598-06');
INSERT INTO public.ligas_miembros_aud VALUES ('77433993-7e30-49f7-a78b-e7d6f41120a2', 'b5af3f63-b5b7-4632-b166-b90a8bc26081', 'c956bff1-92b2-4f74-85cc-cfa0dc99e3b9', 'unirse', '2025-10-22 12:46:07.512595-06');
INSERT INTO public.ligas_miembros_aud VALUES ('f4f2c70f-d13b-4a6d-adeb-0063d9d77e39', 'b5af3f63-b5b7-4632-b166-b90a8bc26081', '80477dbd-86eb-467c-976e-648d55ba0def', 'unirse', '2025-10-22 12:50:09.007501-06');
INSERT INTO public.ligas_miembros_aud VALUES ('96b4815d-3d7c-4087-aa15-50ecafb097a1', 'b5af3f63-b5b7-4632-b166-b90a8bc26081', 'dfd20583-861c-453f-a1cb-161b75e73220', 'unirse', '2025-10-22 12:50:19.393753-06');
INSERT INTO public.ligas_miembros_aud VALUES ('18c72e59-45ab-4510-ba4f-5038b5b74d47', 'b5af3f63-b5b7-4632-b166-b90a8bc26081', '18e11ec2-59e1-49f5-8567-e4db170cf115', 'unirse', '2025-10-22 12:50:27.941238-06');
INSERT INTO public.ligas_miembros_aud VALUES ('838a8b50-f2a1-47d3-b4b4-36b9199a88a0', 'b5af3f63-b5b7-4632-b166-b90a8bc26081', 'ad2b73ce-5c35-4541-9b02-2bdfa046ab90', 'unirse', '2025-10-22 12:53:09.063805-06');
INSERT INTO public.ligas_miembros_aud VALUES ('7394dd17-f35e-4961-bd30-b3c372494ee9', '6d834883-b204-4e08-b80f-657ca39d3be6', 'df891b68-555b-4dca-bbbf-cb963dc25f48', 'unirse', '2025-11-07 20:04:11.723826-06');
INSERT INTO public.ligas_miembros_aud VALUES ('f922726d-2b2c-4785-af59-c9aaa80f91e9', '6d834883-b204-4e08-b80f-657ca39d3be6', 'f40e354d-1bf7-4b3e-9caa-fc234db264ac', 'unirse', '2025-11-07 20:05:21.004626-06');


--
-- TOC entry 3729 (class 0 OID 17091)
-- Dependencies: 222
-- Data for Name: media; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 3730 (class 0 OID 17304)
-- Dependencies: 223
-- Data for Name: temporadas; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.temporadas VALUES ('b0ffc62f-e6da-45cf-bff9-ba260b168556', 'Temporada invierno', 4, '2025-10-22', '2025-11-22', true, '2025-10-21 19:24:52.796524-06');


--
-- TOC entry 3732 (class 0 OID 17387)
-- Dependencies: 225
-- Data for Name: temporadas_semanas; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 3727 (class 0 OID 17049)
-- Dependencies: 220
-- Data for Name: usuarios; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.usuarios VALUES ('80477dbd-86eb-467c-976e-648d55ba0def', 'Test Usuario', 'testuser', 'test@example.com', '$2b$12$Ut.TL4vry8TZxZ2I4bpbo.yU1ViDpcHM6ItGScTkqBFdd.v0z0orS', 'manager', 'activa', 'Ingles', '/img/perfil/default.png', '2025-10-12 13:24:22.249779-06', 0);
INSERT INTO public.usuarios VALUES ('dfd20583-861c-453f-a1cb-161b75e73220', 'Test User ac48ed41', 'testuserac48ed41', 'testac48ed41@example.com', '$2b$12$kZep/BLlGHqMQWVJzRcGN.4EnuouKmkW8YJxlJ//CibGikIDOtG82', 'manager', 'activa', 'Ingles', '/img/perfil/default.png', '2025-10-12 13:29:29.367503-06', 1);
INSERT INTO public.usuarios VALUES ('18e11ec2-59e1-49f5-8567-e4db170cf115', 'pepso', 'usuariopep2', 'userpepo@example.com', '$2b$12$MOP6iGO.hv0o..pjuXxzbuXJg.fwhDeeK.gW1nNoawXe.QVDjkq0K', 'manager', 'activa', 'Ingles', '/img/perfil/default.png', '2025-10-12 14:27:22.309784-06', 0);
INSERT INTO public.usuarios VALUES ('ad2b73ce-5c35-4541-9b02-2bdfa046ab90', 'pepso3', 'usuariopep3', 'userpepo3@example.com', '$2b$12$7QDGjP2gfAHp7The/GJdj.ORawNvTKD2mBmsS8QFHvAKI.4xRbboa', 'manager', 'activa', 'Ingles', '/img/perfil/default.png', '2025-10-12 14:33:50.951997-06', 0);
INSERT INTO public.usuarios VALUES ('f40e354d-1bf7-4b3e-9caa-fc234db264ac', 'Uriza', 'UrizaAndres', 'urizaandres@gmail.com', '$2b$12$fguw75Sa8mg0SPKctewbWOI6wDOaP/qr5NPsb9oYLojk5qZ1z2AoC', 'manager', 'activa', 'en', '/img/perfil/default.png', '2025-10-12 21:54:18.038853-06', 0);
INSERT INTO public.usuarios VALUES ('0cb889cf-8447-4d25-8e01-69796a9a22a0', 'Abner', 'Abner Test 2', 'abnerarroyoquesada@gmail.com', '$2b$12$WBlVYpoW1r779X0/e3LL2uI2.mfghYa9pk/bY3t4xEnDbHa6hIrx.', 'manager', 'activa', 'Ingles', '/img/perfil/default.png', '2025-10-14 14:14:07.356729-06', 0);
INSERT INTO public.usuarios VALUES ('d2dda7a2-6dc4-45dd-aaa2-7912f22a3707', 'Sebas', 'Sebas', 'sebas@correo.com', '$2b$12$ZzHmXr89pmpiFzrxvvPESODq8WsO21OLAQ9RQugZSknUQCNoHa40K', 'manager', 'activa', 'Ingles', '/img/perfil/default.png', '2025-10-14 14:40:24.739153-06', 0);
INSERT INTO public.usuarios VALUES ('97bbed1d-79da-49f8-bc2c-24a1412c5fe8', 'Sprint2', 'Sprint2', 'sprint2@gmail.com', '$2b$12$R7iYDC/7d1MiNk.oYWKMbe623vmjA5DXjKuYz9Ox4fEni/QaYvXNe', 'manager', 'activa', 'Ingles', '/img/perfil/default.png', '2025-10-14 18:08:00.414684-06', 0);
INSERT INTO public.usuarios VALUES ('512bcfde-45b8-4b79-bd62-f6d12e0be400', 'pep', 'elpep', 'userpep@example.com', '$2b$12$HrHlnK29/l4/s01grVpi8uWDjZyiOgaYZZh5Hg7V.R.5wh39U1zuW', 'manager', 'bloqueado', 'Ingles', '/img/perfil/default.png', '2025-10-12 13:29:56.728135-06', 5);
INSERT INTO public.usuarios VALUES ('1ff82d17-3bbb-40eb-a57a-924432ca1980', 'Sebas', 'Usuario', 'sebashb04@hotmail.com', '$2b$12$J8iTuaUOZ2nDOTlpFzDEze0QR13HmftnzhJDKR0A1MwgVpihmeQ..', 'manager', 'activa', 'Ingles', '/img/perfil/default.png', '2025-10-14 18:12:44.441617-06', 0);
INSERT INTO public.usuarios VALUES ('df891b68-555b-4dca-bbbf-cb963dc25f48', 'Abner Arroyo Quesada', 'abner2111', 'abneraq73@gmail.com', '$2b$12$cI2mUvwo2GWVQ6q8Yct6suY3JWZ/kAGx4lfvhQ/kg5LsDOU9fU3Fe', 'manager', 'activa', 'es', '/img/perfil/default.png', '2025-10-12 15:07:09.102713-06', 0);
INSERT INTO public.usuarios VALUES ('50caccc0-a1d8-48c0-99cd-59478a46d522', 'Uriza post test', 'string', 'urizatest@example.com', '$2b$12$4P9FoBjd6Dk2OEIn01AH8OUxE/y7zzWQ8FUiBY/BLMEFu5BHicMUG', 'manager', 'activa', 'Ingles', '/img/perfil/default.png', '2025-10-23 20:44:23.639548-06', 0);
INSERT INTO public.usuarios VALUES ('c956bff1-92b2-4f74-85cc-cfa0dc99e3b9', 'Abner', 'abner2111', 'abneraq72@gmail.com', '$2b$12$zwPmN/KPAymnoQDFZ4vyWuHsx2uPJaqtNJQPrGmXSZK3BKj0RlbMG', 'manager', 'activa', 'Ingles', '/img/perfil/default.png', '2025-10-12 15:19:20.072557-06', 0);


--
-- TOC entry 3564 (class 2606 OID 25626)
-- Name: equipos_fantasy_audit equipos_fantasy_audit_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.equipos_fantasy_audit
    ADD CONSTRAINT equipos_fantasy_audit_pkey PRIMARY KEY (id);


--
-- TOC entry 3557 (class 2606 OID 25605)
-- Name: equipos_fantasy equipos_fantasy_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.equipos_fantasy
    ADD CONSTRAINT equipos_fantasy_pkey PRIMARY KEY (id);


--
-- TOC entry 3553 (class 2606 OID 25569)
-- Name: jugadores jugadores_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.jugadores
    ADD CONSTRAINT jugadores_pkey PRIMARY KEY (id);


--
-- TOC entry 3551 (class 2606 OID 17433)
-- Name: ligas_miembros_aud ligas_miembros_aud_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ligas_miembros_aud
    ADD CONSTRAINT ligas_miembros_aud_pkey PRIMARY KEY (id);


--
-- TOC entry 3540 (class 2606 OID 17374)
-- Name: ligas ligas_nombre_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ligas
    ADD CONSTRAINT ligas_nombre_key UNIQUE (nombre);


--
-- TOC entry 3542 (class 2606 OID 17372)
-- Name: ligas ligas_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ligas
    ADD CONSTRAINT ligas_pkey PRIMARY KEY (id);


--
-- TOC entry 3533 (class 2606 OID 17099)
-- Name: media media_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.media
    ADD CONSTRAINT media_pkey PRIMARY KEY (equipo_id);


--
-- TOC entry 3546 (class 2606 OID 17410)
-- Name: ligas_miembros pk_liga_miembro; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ligas_miembros
    ADD CONSTRAINT pk_liga_miembro PRIMARY KEY (liga_id, usuario_id);


--
-- TOC entry 3544 (class 2606 OID 17392)
-- Name: temporadas_semanas pk_temp_sem; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.temporadas_semanas
    ADD CONSTRAINT pk_temp_sem PRIMARY KEY (temporada_id, numero);


--
-- TOC entry 3535 (class 2606 OID 17313)
-- Name: temporadas temporadas_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.temporadas
    ADD CONSTRAINT temporadas_pkey PRIMARY KEY (id);


--
-- TOC entry 3548 (class 2606 OID 17412)
-- Name: ligas_miembros uq_alias_por_liga; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ligas_miembros
    ADD CONSTRAINT uq_alias_por_liga UNIQUE (liga_id, alias);


--
-- TOC entry 3555 (class 2606 OID 25571)
-- Name: jugadores uq_jugador_por_equipo; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.jugadores
    ADD CONSTRAINT uq_jugador_por_equipo UNIQUE (equipo_id, nombre);


--
-- TOC entry 3562 (class 2606 OID 25607)
-- Name: equipos_fantasy uq_nombre_equipo_fantasy_por_liga; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.equipos_fantasy
    ADD CONSTRAINT uq_nombre_equipo_fantasy_por_liga UNIQUE (liga_id, nombre);


--
-- TOC entry 3538 (class 2606 OID 17315)
-- Name: temporadas uq_temporadas_nombre; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.temporadas
    ADD CONSTRAINT uq_temporadas_nombre UNIQUE (nombre);


--
-- TOC entry 3529 (class 2606 OID 17067)
-- Name: usuarios usuarios_correo_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_correo_key UNIQUE (correo);


--
-- TOC entry 3531 (class 2606 OID 17065)
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id);


--
-- TOC entry 3565 (class 1259 OID 25640)
-- Name: idx_equipos_fantasy_audit_equipo; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_equipos_fantasy_audit_equipo ON public.equipos_fantasy_audit USING btree (equipo_fantasy_id);


--
-- TOC entry 3566 (class 1259 OID 25642)
-- Name: idx_equipos_fantasy_audit_timestamp; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_equipos_fantasy_audit_timestamp ON public.equipos_fantasy_audit USING btree (timestamp_accion);


--
-- TOC entry 3567 (class 1259 OID 25641)
-- Name: idx_equipos_fantasy_audit_usuario; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_equipos_fantasy_audit_usuario ON public.equipos_fantasy_audit USING btree (usuario_id);


--
-- TOC entry 3558 (class 1259 OID 25637)
-- Name: idx_equipos_fantasy_liga; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_equipos_fantasy_liga ON public.equipos_fantasy USING btree (liga_id);


--
-- TOC entry 3559 (class 1259 OID 25639)
-- Name: idx_equipos_fantasy_nombre; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_equipos_fantasy_nombre ON public.equipos_fantasy USING btree (nombre);


--
-- TOC entry 3560 (class 1259 OID 25638)
-- Name: idx_equipos_fantasy_usuario; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_equipos_fantasy_usuario ON public.equipos_fantasy USING btree (usuario_id);


--
-- TOC entry 3536 (class 1259 OID 17386)
-- Name: uq_temporada_actual; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_temporada_actual ON public.temporadas USING btree (es_actual) WHERE (es_actual = true);


--
-- TOC entry 3549 (class 1259 OID 17423)
-- Name: uq_unico_comisionado_por_liga; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_unico_comisionado_por_liga ON public.ligas_miembros USING btree (liga_id) WHERE (rol = 'Comisionado'::public.rol_membresia);


--
-- TOC entry 3579 (class 2620 OID 17385)
-- Name: ligas trg_ligas_actualizado; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_ligas_actualizado BEFORE UPDATE ON public.ligas FOR EACH ROW EXECUTE FUNCTION public.trg_set_actualizado_liga();


--
-- TOC entry 3580 (class 2620 OID 25646)
-- Name: equipos_fantasy trigger_audit_equipos_fantasy; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trigger_audit_equipos_fantasy AFTER INSERT OR DELETE OR UPDATE ON public.equipos_fantasy FOR EACH ROW EXECUTE FUNCTION public.audit_equipos_fantasy_changes();


--
-- TOC entry 3581 (class 2620 OID 25644)
-- Name: equipos_fantasy update_equipos_fantasy_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_equipos_fantasy_updated_at BEFORE UPDATE ON public.equipos_fantasy FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 3577 (class 2606 OID 25627)
-- Name: equipos_fantasy_audit equipos_fantasy_audit_equipo_fantasy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.equipos_fantasy_audit
    ADD CONSTRAINT equipos_fantasy_audit_equipo_fantasy_id_fkey FOREIGN KEY (equipo_fantasy_id) REFERENCES public.equipos_fantasy(id) ON DELETE CASCADE;


--
-- TOC entry 3578 (class 2606 OID 25632)
-- Name: equipos_fantasy_audit equipos_fantasy_audit_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.equipos_fantasy_audit
    ADD CONSTRAINT equipos_fantasy_audit_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id) ON DELETE RESTRICT;


--
-- TOC entry 3575 (class 2606 OID 25608)
-- Name: equipos_fantasy equipos_fantasy_liga_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.equipos_fantasy
    ADD CONSTRAINT equipos_fantasy_liga_id_fkey FOREIGN KEY (liga_id) REFERENCES public.ligas(id) ON DELETE CASCADE;


--
-- TOC entry 3576 (class 2606 OID 25613)
-- Name: equipos_fantasy equipos_fantasy_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.equipos_fantasy
    ADD CONSTRAINT equipos_fantasy_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id) ON DELETE RESTRICT;


--
-- TOC entry 3568 (class 2606 OID 17380)
-- Name: ligas ligas_comisionado_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ligas
    ADD CONSTRAINT ligas_comisionado_id_fkey FOREIGN KEY (comisionado_id) REFERENCES public.usuarios(id) ON DELETE RESTRICT;


--
-- TOC entry 3573 (class 2606 OID 17434)
-- Name: ligas_miembros_aud ligas_miembros_aud_liga_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ligas_miembros_aud
    ADD CONSTRAINT ligas_miembros_aud_liga_id_fkey FOREIGN KEY (liga_id) REFERENCES public.ligas(id) ON DELETE CASCADE;


--
-- TOC entry 3574 (class 2606 OID 17439)
-- Name: ligas_miembros_aud ligas_miembros_aud_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ligas_miembros_aud
    ADD CONSTRAINT ligas_miembros_aud_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id) ON DELETE CASCADE;


--
-- TOC entry 3571 (class 2606 OID 17413)
-- Name: ligas_miembros ligas_miembros_liga_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ligas_miembros
    ADD CONSTRAINT ligas_miembros_liga_id_fkey FOREIGN KEY (liga_id) REFERENCES public.ligas(id) ON DELETE CASCADE;


--
-- TOC entry 3572 (class 2606 OID 17418)
-- Name: ligas_miembros ligas_miembros_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ligas_miembros
    ADD CONSTRAINT ligas_miembros_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id) ON DELETE CASCADE;


--
-- TOC entry 3569 (class 2606 OID 17375)
-- Name: ligas ligas_temporada_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ligas
    ADD CONSTRAINT ligas_temporada_id_fkey FOREIGN KEY (temporada_id) REFERENCES public.temporadas(id) ON DELETE RESTRICT;


--
-- TOC entry 3570 (class 2606 OID 17393)
-- Name: temporadas_semanas temporadas_semanas_temporada_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.temporadas_semanas
    ADD CONSTRAINT temporadas_semanas_temporada_id_fkey FOREIGN KEY (temporada_id) REFERENCES public.temporadas(id) ON DELETE CASCADE;


-- Completed on 2025-11-08 12:43:38 CST

--
-- PostgreSQL database dump complete
--

\unrestrict vWBpLli6Raw0bKVaLvMEdh9iNM4ycEAv9FbHFlpRFU7immuRYNGG4gZZDh5nUZJ

