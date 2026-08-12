CREATE TABLE "user" (
    "id" BIGSERIAL PRIMARY KEY NOT NULL,
    "phone_number" VARCHAR(31) NOT NULL,
    "password" VARCHAR(255) NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "city" VARCHAR(255) NOT NULL,
    "avatar_link" VARCHAR(1023) NOT NULL,
    "description" TEXT NOT NULL
);

CREATE TABLE "reviev" (
    "id" BIGSERIAL PRIMARY KEY NOT NULL,
    "comment" TEXT,
    "rate" INTEGER NOT NULL,
    "user_id" BIGINT NOT NULL REFERENCES "user"(id)
);

CREATE TABLE "category" (
    "id" BIGSERIAL PRIMARY KEY NOT NULL,
    "title" VARCHAR(255) NOT NULL
);

CREATE TABLE "advertisement" (
    "id" BIGSERIAL PRIMARY KEY NOT NULL,
    "type" BOOLEAN NOT NULL,
    "category_id" BIGINT NOT NULL REFERENCES "category"(id),
    "title" VARCHAR(255) NOT NULL,
    "description" TEXT NOT NULL,
    "price" INTEGER NOT NULL,
    "city" VARCHAR(255) NOT NULL,
    "user_id" BIGINT NOT NULL REFERENCES "user"(id),
    "contractor_id" BIGINT NOT NULL REFERENCES "user"(id),
    "desired_date" TIMESTAMP,
    "creation_date" TIMESTAMP NOT NULL
);

CREATE TABLE "chat" (
    "id" BIGSERIAL PRIMARY KEY NOT NULL,
    "advertisement_id" BIGINT NOT NULL REFERENCES "advertisement"(id),
    "sender_id" BIGINT NOT NULL REFERENCES "user"(id)
);

CREATE TABLE "message" (
    "id" BIGSERIAL PRIMARY KEY NOT NULL,
    "message_text" TEXT NOT NULL,
    "user_id" BIGINT NOT NULL REFERENCES "user"(id),
    "chat_id" BIGINT NOT NULL REFERENCES "chat"(id)
);

CREATE TABLE "operation" (
    "id" BIGSERIAL PRIMARY KEY NOT NULL,
    "sender_id" BIGINT NOT NULL REFERENCES "user"(id),
    "user_id" BIGINT NOT NULL REFERENCES "user"(id),
    "advertisement_id" BIGINT NOT NULL REFERENCES "advertisement"(id),
    "hours_amount" INTEGER NOT NULL
)