# Django Project Portfolio

This repository contains multiple class apps.  
The final project work is in the `project` app.

## Project App Features

- Data models: `Artist`, `Album`, `Listener`, `Review`
- Relationships:
  - One artist has many albums
  - One listener can write many reviews
  - One album can have many reviews
- Generic views:
  - List/detail pages for artists, albums, and listeners
  - Review list page
  - Create, edit, and delete review forms
- Interaction features:
  - Album filtering by genre and year
  - Dashboard counts and top-rated album section
- UI:
  - Shared navigation template and custom CSS styling

## How to Run

1. Activate your virtual environment.
2. Run migrations:
   - `python manage.py migrate`
3. Start server:
   - `python manage.py runserver`
4. Open:
   - `http://127.0.0.1:8000/project/`

## Documentation Notes

- Core logic is documented with module/class docstrings in `project/views.py` and `project/forms.py`.
- Admin setup with list views is in `project/admin.py`.
