import factory
from models import Movie


class MovieFactory(factory.Factory):
    class Meta:
        model = Movie

    barcode = factory.Faker.pr('ean13')
    
if __name__ == '__main__':
 # Initialize Faker with a seed for reproducibility (optional)
# Replace 'your_seed_here' with an integer seed or None

    # Create a single instance with random data
    movie_factory = MovieFactory()

    # Create multiple instances with random data
    movie_factory.create_batch(10)

    