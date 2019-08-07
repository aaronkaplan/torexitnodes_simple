--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'SQL_ASCII';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;



create database tordb_simple;
\c tordb_simple

--
-- Name: nodes; Type: TABLE; Schema: public; Owner: aaron; Tablespace: 
--

-- all data comes from https://check.torproject.org/exit-addresses
-- this as of now seems to be the only accurate / official source

CREATE TABLE node (
    node_id varchar(42),
    ip inet,
    first_published timestamp with time zone,
    last_status timestamp with time zone,
    exit_address_ts timestamp with time zone,
    id_nodetype integer default 1       -- 1 == exit node, 2 == relay , 3 == bridge
);


ALTER TABLE public.node OWNER TO aaron;


create index idx_node_ip on node(ip);
create index idx_node_exit_address_ts on node(exit_address_ts);
create index idx_node_first_published on node(first_published);
create index idx_node_exit_last_status on node(last_status);

create unique index idx_node_combined on node (node_id, ip, exit_address_ts, id_nodetype);

create sequence seq_nodetype_id;

--
-- Name: nodetype; Type: TABLE; Schema: public; Owner: aaron; Tablespace: 
--

CREATE TABLE nodetype (
    id integer NOT NULL default nextval('seq_nodetype_id'),
    type character varying(100)
);


ALTER TABLE public.nodetype OWNER TO aaron;


--
-- Data for Name: nodetype; Type: TABLE DATA; Schema: public; Owner: aaron
--

COPY nodetype (id, type) FROM stdin;
1	exitnode
2	relay
3	bridge
\.



--
-- Name: nodetype_pkey; Type: CONSTRAINT; Schema: public; Owner: aaron; Tablespace: 
--

ALTER TABLE ONLY nodetype
    ADD CONSTRAINT nodetype_pkey PRIMARY KEY (id);


--
-- Name: node_id_nodetype_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aaron
--

ALTER TABLE ONLY node
    ADD CONSTRAINT node_id_nodetype_fkey FOREIGN KEY (id_nodetype) REFERENCES nodetype(id);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

