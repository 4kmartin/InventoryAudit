from distutils.core import setup

setup(
    name="Inventory Audit",
    version= "0.1",
    description="Collects inventories from disparent databases for comparison",
    author="Anthany Martin",
    author_email="4kmartin@gmail.com",
    packages=["PyTenable", "pysqlite3","requests-oauthlib","oauthlib","pyyaml"]
)
