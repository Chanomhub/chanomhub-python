import unittest
from unittest.mock import MagicMock
import sys
import os

# Add the python directory to sys.path
sys.path.append(os.path.join(os.getcwd(), 'python'))

from chanomhub import ChanomhubClient, ChanomhubConfig, ArticleRepository
from chanomhub.models.article import ArticleListOptions, ArticleFilter

class TestArticleRepository(unittest.TestCase):
    def setUp(self):
        self.config = ChanomhubConfig(api_url="https://api.example.com")
        self.client = ChanomhubClient(self.config)
        self.client.graphql_fetch = MagicMock()
        self.client.rest_fetch = MagicMock()
        self.repo = ArticleRepository(self.client)

    def test_get_all_articles(self):
        self.client.graphql_fetch.return_value = {
            "public": {
                "articles": [
                    {
                        "id": 1,
                        "title": "Test Article",
                        "slug": "test-article",
                        "description": "A test article",
                        "createdAt": "2024-01-01T00:00:00Z",
                        "updatedAt": "2024-01-01T00:00:00Z",
                        "status": "PUBLISHED",
                        "author": {"name": "Test Author", "image": None},
                        "price": 0,
                        "isPaid": False,
                        "isUnlocked": True,
                        "viewsCount": 100
                    }
                ]
            }
        }
        
        articles = self.repo.get_all()
        
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0].title, "Test Article")
        self.assertEqual(articles[0].slug, "test-article")
        self.client.graphql_fetch.assert_called_once()

    def test_get_by_slug(self):
        self.client.graphql_fetch.return_value = {
            "public": {
                "article": {
                    "id": 1,
                    "title": "Test Article",
                    "slug": "test-article",
                    "description": "A test article",
                    "createdAt": "2024-01-01T00:00:00Z",
                    "updatedAt": "2024-01-01T00:00:00Z",
                    "status": "PUBLISHED",
                    "author": {"id": 1, "name": "Test Author", "bio": "Bio", "image": "author.png"},
                    "price": 0,
                    "isPaid": False,
                    "isUnlocked": True,
                    "viewsCount": 100,
                    "downloads": [
                        {
                            "id": 1,
                            "name": "Download 1",
                            "url": "public/file.zip",
                            "isActive": True,
                            "vipOnly": False,
                            "type": "DIRECT_FILE"
                        }
                    ]
                }
            }
        }
        
        article = self.repo.get_by_slug("test-article")
        
        self.assertIsNotNone(article)
        self.assertEqual(article.title, "Test Article")
        self.assertEqual(len(article.downloads), 1)
        self.assertEqual(article.downloads[0].url, "https://storage.chanomhub.com/public/file.zip")
        self.assertTrue(article.downloads[0].is_direct_file)

if __name__ == '__main__':
    unittest.main()
