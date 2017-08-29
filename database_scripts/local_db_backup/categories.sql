--
-- PostgreSQL database dump
--

-- Dumped from database version 9.1.24
-- Dumped by pg_dump version 9.1.24
-- Started on 2017-05-02 00:12:03 BRT

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 197 (class 1259 OID 24715)
-- Dependencies: 8
-- Name: categories_categories; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE categories_categories (
    id integer NOT NULL,
    categories_text character varying(200) NOT NULL
);


ALTER TABLE public.categories_categories OWNER TO postgres;

--
-- TOC entry 196 (class 1259 OID 24713)
-- Dependencies: 197 8
-- Name: categories_categories_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE categories_categories_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.categories_categories_id_seq OWNER TO postgres;

--
-- TOC entry 3688 (class 0 OID 0)
-- Dependencies: 196
-- Name: categories_categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE categories_categories_id_seq OWNED BY categories_categories.id;


--
-- TOC entry 3571 (class 2604 OID 24718)
-- Dependencies: 196 197 197
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY categories_categories ALTER COLUMN id SET DEFAULT nextval('categories_categories_id_seq'::regclass);


--
-- TOC entry 3683 (class 0 OID 24715)
-- Dependencies: 197 3684
-- Data for Name: categories_categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY categories_categories (id, categories_text) FROM stdin;
2	SERVICES
3	RIDESHARE
1	PRODUCTS
4	HOUSING
\.


--
-- TOC entry 3689 (class 0 OID 0)
-- Dependencies: 196
-- Name: categories_categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('categories_categories_id_seq', 1, false);


--
-- TOC entry 3573 (class 2606 OID 24720)
-- Dependencies: 197 197 3685
-- Name: categories_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY categories_categories
    ADD CONSTRAINT categories_categories_pkey PRIMARY KEY (id);


-- Completed on 2017-05-02 00:12:04 BRT

--
-- PostgreSQL database dump complete
--

