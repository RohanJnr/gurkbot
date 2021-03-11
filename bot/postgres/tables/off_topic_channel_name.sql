CREATE TABLE public.off_topic_channel_name (
	channel_name varchar(256) NOT NULL,
	created_at TIMESTAMP NOT NULL DEFAULT now(),
	CONSTRAINT off_topic_channel_name_pk PRIMARY KEY (channel_name)
);
