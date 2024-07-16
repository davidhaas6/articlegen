import unittest
from unittest.mock import patch, MagicMock
import os
from datetime import datetime

import sys; sys.path.append('../')
import deploy

class TestGenerateAndPushArticles(unittest.TestCase):

    @patch.dict(os.environ, {'GITHUB_PAT': 'dummy_token'})
    def test_get_github_token_success(self):
        token = deploy.get_github_token()
        self.assertEqual(token, 'dummy_token')

    @patch.dict(os.environ, {}, clear=True)
    def test_get_github_token_failure(self):
        with self.assertRaises(ValueError):
            deploy.get_github_token()

    @patch('deploy.gen.new_articles')
    @patch('deploy.job.write_articles')
    @patch('deploy.templater.generate_site')
    @patch('deploy.os.chdir')
    @patch('deploy.subprocess.run')
    @patch('deploy.get_github_token')
    def test_generate_and_push_articles(self, mock_get_token, mock_subprocess, mock_chdir, 
                                        mock_generate_site, mock_write_articles, mock_new_articles):
        # Setup mocks
        mock_new_articles.return_value = ['article1', 'article2']
        mock_generate_site.return_value = '/tmp/site_dir'
        mock_get_token.return_value = 'dummy_token'

        # Call the function
        result = deploy.generate_and_push_articles('https://github.com/username/repo.git', 2)

        # Assertions
        mock_new_articles.assert_called_once_with(2)
        mock_write_articles.assert_called_once()
        mock_generate_site.assert_called_once()
        mock_chdir.assert_called_once_with('/tmp/site_dir')
        self.assertEqual(mock_subprocess.call_count, 5)  # 5 subprocess calls
        self.assertEqual(result, '/tmp/site_dir')

    @patch.dict(os.environ, {'GITHUB_REPO_URL': 'https://github.com/username/repo.git'})
    @patch('deploy.generate_and_push_articles')
    def test_main(self, mock_generate_and_push):
        deploy.main()
        mock_generate_and_push.assert_called_once_with('https://github.com/username/repo.git', 5)

    @patch.dict(os.environ, {}, clear=True)
    def test_main_no_repo_url(self):
        with self.assertRaises(ValueError):
            deploy.main()

if __name__ == '__main__':
    unittest.main()