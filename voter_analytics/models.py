import csv
from datetime import datetime
from django.db import models  # keep this

class Voter(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    street_number = models.CharField(max_length=10)
    street_name = models.CharField(max_length=200)
    apartment_number = models.CharField(max_length=20, blank=True, null=True)
    zip_code = models.CharField(max_length=10)
    date_of_birth = models.DateField(null=True)           # allow nulls
    date_of_registration = models.DateField(null=True)   # allow nulls
    party_affiliation = models.CharField(max_length=2)
    precinct_number = models.IntegerField()
    v20state = models.BooleanField()
    v21town = models.BooleanField()
    v21primary = models.BooleanField()
    v22general = models.BooleanField()
    v23town = models.BooleanField()
    voter_score = models.IntegerField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


def load_data():
    file_path = '/Users/krishashetty/Downloads/newton_voters.csv'

    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:

            # Handle dates safely
            dob_str = row['Date of Birth']
            reg_str = row['Date of Registration']

            try:
                date_of_birth = datetime.strptime(dob_str, '%Y-%m-%d').date()
            except ValueError:
                date_of_birth = None

            try:
                date_of_registration = datetime.strptime(reg_str, '%Y-%m-%d').date()
            except ValueError:
                date_of_registration = None

            def parse_bool(val):
                return str(val).strip().upper() == 'TRUE'

            def parse_int(val, default=0):
                try:
                    return int(val)
                except (ValueError, TypeError):
                    return default

            Voter.objects.create(
                first_name=row['First Name'],
                last_name=row['Last Name'],
                street_number=row['Residential Address - Street Number'],
                street_name=row['Residential Address - Street Name'],
                apartment_number=row['Residential Address - Apartment Number'] or None,
                zip_code=row['Residential Address - Zip Code'],
                date_of_birth=date_of_birth,
                date_of_registration=date_of_registration,
                party_affiliation=row['Party Affiliation'].strip(),
                precinct_number=parse_int(row['Precinct Number']),
                v20state=parse_bool(row['v20state']),
                v21town=parse_bool(row['v21town']),
                v21primary=parse_bool(row['v21primary']),
                v22general=parse_bool(row['v22general']),
                v23town=parse_bool(row['v23town']),
                voter_score=parse_int(row['voter_score']),
            )

    print("Data load complete!")