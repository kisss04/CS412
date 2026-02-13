from django.core.management.base import BaseCommand
from datetime import date
from mini_insta.models import Profile


class Command(BaseCommand):
    help = "Add sample profiles to Mini Insta"

    def handle(self, *args, **options):
        samples = [
            {
                "username": "taylor_swift",
                "display_name": "Taylor Swift",
                "profile_image_url": "https://cs-people.bu.edu/azs/images/taylor_swift.jpg",
                "bio_text": "Singer-songwriter. 13 Grammy Awards. Cat mom.",
                "join_date": date(2020, 1, 15),
            },
            {
                "username": "spongebob",
                "display_name": "SpongeBob SquarePants",
                "profile_image_url": "https://i.ytimg.com/vi/9qVn-X4gsHk/maxresdefault.jpg",
                "bio_text": "Living in a pineapple under the sea.",
                "join_date": date(1999, 5, 1),
            },
            {
                "username": "Patrick",
                "display_name": "patrickstar",
                "profile_image_url": "https://pyxis.nymag.com/v1/imgs/44d/13c/0ed4363f89e451cde26e4bfe48730be61f-patrick-star.jpg",
                "bio_text": "chilling with the spongebobbbbb!.",
                "join_date": date(2025, 2, 1),
            },
        ]
        for data in samples:
            obj, created = Profile.objects.update_or_create(
                username=data["username"],
                defaults=data,
            )
            status = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{status}: {obj.username}"))
