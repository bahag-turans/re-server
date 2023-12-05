CREATE TABLE users
(
    userid integer NOT NULL GENERATED BY DEFAULT AS IDENTITY ( INCREMENT 1 START 100 ),
    full_name character varying(100)  NOT NULL,
    email character varying(100)  NOT NULL,
    phone_number character varying(100),
    CONSTRAINT user_pkey PRIMARY KEY (userid)
)
