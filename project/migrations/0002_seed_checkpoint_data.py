from django.db import migrations


def seed_data(apps, schema_editor):
    Artist = apps.get_model("project", "Artist")
    Album = apps.get_model("project", "Album")
    Listener = apps.get_model("project", "Listener")
    Review = apps.get_model("project", "Review")

    if Artist.objects.exists():
        return

    artists = [
        Artist(
            name="Taylor Swift",
            genre="Pop / Country",
            origin_country="United States",
            bio="Singer-songwriter known for narrative songwriting.",
        ),
        Artist(
            name="Bad Bunny",
            genre="Latin trap / Reggaeton",
            origin_country="Puerto Rico",
            bio="Rapper and singer; global streaming leader.",
        ),
        Artist(
            name="The Beatles",
            genre="Rock",
            origin_country="United Kingdom",
            bio="Influential 1960s rock band from Liverpool.",
        ),
        Artist(
            name="Beyoncé",
            genre="R&B / Pop",
            origin_country="United States",
            bio="Singer, producer, and performer.",
        ),
    ]
    Artist.objects.bulk_create(artists)
    artists = list(Artist.objects.order_by("id"))

    listeners = [
        Listener(first_name="Alex", last_name="Rivera", email="alex.rivera@example.com"),
        Listener(first_name="Jordan", last_name="Kim", email="j.kim@example.com"),
        Listener(first_name="Sam", last_name="Patel", email="sam.patel@example.com"),
        Listener(first_name="Riley", last_name="Nguyen", email="r.nguyen@example.com"),
        Listener(first_name="Morgan", last_name="Lee", email="morgan.lee@example.com"),
    ]
    Listener.objects.bulk_create(listeners)
    listeners = list(Listener.objects.order_by("id"))

    albums = [
        Album(
            title="Midnights",
            artist=artists[0],
            year_released=2022,
            genre="Pop",
        ),
        Album(
            title="Un Verano Sin Ti",
            artist=artists[1],
            year_released=2022,
            genre="Reggaeton",
        ),
        Album(
            title="Abbey Road",
            artist=artists[2],
            year_released=1969,
            genre="Rock",
        ),
        Album(
            title="Renaissance",
            artist=artists[3],
            year_released=2022,
            genre="House / R&B",
        ),
    ]
    Album.objects.bulk_create(albums)
    albums = list(Album.objects.order_by("id"))

    Review.objects.bulk_create(
        [
            Review(
                album=albums[0],
                listener=listeners[0],
                rating=9,
                review_text="Dreamy production and sharp lyrics.",
            ),
            Review(
                album=albums[1],
                listener=listeners[1],
                rating=10,
                review_text="Perfect summer album; huge variety.",
            ),
            Review(
                album=albums[2],
                listener=listeners[2],
                rating=10,
                review_text="Classic from start to finish.",
            ),
            Review(
                album=albums[3],
                listener=listeners[3],
                rating=8,
                review_text="Bold and dance-forward.",
            ),
            Review(
                album=albums[0],
                listener=listeners[4],
                rating=8,
                review_text="Grows on you after a few listens.",
            ),
        ]
    )


def unseed_data(apps, schema_editor):
    Artist = apps.get_model("project", "Artist")
    Artist.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("project", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_data, unseed_data),
    ]
