-- -- run "sqlite3 movieratings.db" to start the database up

-- create table schema
drop table if exists votes;

create table votes(
	uuid TEXT PRIMARY KEY,
	county TEXT,
	precinct TEXT, 
	round INTEGER,
	buttigieg_votes INTEGER,
	warren_votes INTEGER,
	klobuchar_votes INTEGER,
	biden_votes INTEGER,
	yang_votes INTEGER,
	sanders_votes INTEGER,
	steyer_votes INTEGER,
	gabbard_votes INTEGER,
	other_votes INTEGER,
	uncommitted_votes INTEGER

	CHECK(precinct IS NOT NULL 
		AND county IS NOT NULL 
		AND round IS NOT NULL)
);

-- -- create table schema
-- drop table if exists precinct_d;

-- create table precinct_d(
-- 	county TEXT,
-- 	precinct TEXT,
-- 	CD2SDE REAL

-- 	CHECK(precinct IS NOT NULL)
-- );


drop table if exists results;

create table results(
	county TEXT,
	precinct TEXT,
	buttigieg_votes INTEGER,
	warren_votes INTEGER,
	klobuchar_votes INTEGER,
	biden_votes INTEGER,
	yang_votes INTEGER,
	sanders_votes INTEGER,
	steyer_votes INTEGER,
	gabbard_votes INTEGER,
	other_votes INTEGER,
	uncommitted_votes INTEGER,
	-- sdes
	buttigieg_sde INTEGER,
	warren_sde INTEGER,
	klobuchar_sde INTEGER,
	biden_sde INTEGER,
	yang_sde INTEGER,
	sanders_sde INTEGER,
	steyer_sde INTEGER,
	gabbard_sde INTEGER,
	other_sde INTEGER,
	uncommitted_sde INTEGER
);

-- drop table if exists candidates;

-- create table candidates(
-- 	candidate_id INTEGER PRIMARY KEY,
-- 	candidate_first_name TEXT,
-- 	candidate_last_name TEXT
-- );


-- drop table if exists security;

-- create table security(
-- 	username TEXT PRIMARY KEY,
-- 	precinct TEXT,
-- 	password TEXT);



