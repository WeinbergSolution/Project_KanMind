# Models

## User

- fullname
- email
- passwort

**Fertig**

## Board

- title -> String
- owner -> (DK auf User)
- members -> (many to many field auf user)

## Task

- board -> (als FK auf Board)
- title -> string
- description -> string
- status -> Auswahl (to-do`, `in-progress`, `review`oder`done`)
- priority -> Auswahl (low`, `medium`oder`high`)
- assignee -> (als FK auf User definieren)
- reviewer -> (als FK auf User definieren)
- due_date -> Datum

## Comment

klicke in die erste GEt

- created_at -> Datum
- author -> (al FK auf USer definieren )
- content -> string
- task -> (als FK auf Task definieren)
