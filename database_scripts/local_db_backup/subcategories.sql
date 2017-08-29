--
-- PostgreSQL database dump
--

-- Dumped from database version 9.1.24
-- Dumped by pg_dump version 9.1.24
-- Started on 2017-05-21 00:29:12 BRT

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 186 (class 1259 OID 25201)
-- Dependencies: 8
-- Name: categories_subcategories; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE categories_subcategories (
    id integer NOT NULL,
    sub_categories_text character varying(220) NOT NULL,
    categories_id integer NOT NULL
);


ALTER TABLE public.categories_subcategories OWNER TO postgres;

--
-- TOC entry 185 (class 1259 OID 25199)
-- Dependencies: 8 186
-- Name: categories_subcategories_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE categories_subcategories_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.categories_subcategories_id_seq OWNER TO postgres;

--
-- TOC entry 3717 (class 0 OID 0)
-- Dependencies: 185
-- Name: categories_subcategories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE categories_subcategories_id_seq OWNED BY categories_subcategories.id;


--
-- TOC entry 3598 (class 2604 OID 26329)
-- Dependencies: 186 185 186
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY categories_subcategories ALTER COLUMN id SET DEFAULT nextval('categories_subcategories_id_seq'::regclass);


--
-- TOC entry 3712 (class 0 OID 25201)
-- Dependencies: 186 3713
-- Data for Name: categories_subcategories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY categories_subcategories (id, sub_categories_text, categories_id) FROM stdin;
2	OTHER	1
3	TRAVEL	1
4	GARDEN	1
5	CLOTHES & ACESSORIES	1
6	FILM & MOVIES	1
7	PETS & ANIMALS	1
8	ELECTRONICS	1
9	FOOD & KITCHEN	1
10	CAMPING & OUTDOORS	1
11	FURNITURE	1
12	GAMES & TOYS	1
13	BOOKS & MAGAZINES	1
14	MUSIC	1
15	SPORTS	1
16	TOOLS	1
1	AUTOMOTIVE	2
17	BEAUTY	2
18	COMPUTER	2
19	CYCLE	2
20	FARM+GARDEN	2
21	FINANCIAL	2
22	HOSUEHOLD	2
23	LABOR	2
24	LEGAL	2
25	TUTORING	2
26	PET	2
27	REAL ESTATE	2
28	SKILLED TRADE	2
31	THERAPEUTIC	2
32	MEDIA	2
34	RIDESHARE	3
35	HOUSING	4
\.


--
-- TOC entry 3718 (class 0 OID 0)
-- Dependencies: 185
-- Name: categories_subcategories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('categories_subcategories_id_seq', 35, true);


--
-- TOC entry 3601 (class 2606 OID 25206)
-- Dependencies: 186 186 3714
-- Name: categories_subcategories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY categories_subcategories
    ADD CONSTRAINT categories_subcategories_pkey PRIMARY KEY (id);


--
-- TOC entry 3599 (class 1259 OID 25212)
-- Dependencies: 186 3714
-- Name: categories_subcategories_09c55841; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX categories_subcategories_09c55841 ON categories_subcategories USING btree (categories_id);


--
-- TOC entry 3602 (class 2606 OID 25207)
-- Dependencies: 186 184 3714
-- Name: cate_categories_id_5ce3763741fd3ceb_fk_categories_categories_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY categories_subcategories
    ADD CONSTRAINT cate_categories_id_5ce3763741fd3ceb_fk_categories_categories_id FOREIGN KEY (categories_id) REFERENCES categories_categories(id) DEFERRABLE INITIALLY DEFERRED;


-- Completed on 2017-05-21 00:29:12 BRT

--
-- PostgreSQL database dump complete
--

