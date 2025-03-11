import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# Add project root to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestMainApplication(unittest.TestCase):
    """Test the main application entry point and Flask app creation"""
    
    @patch('tkinter.Tk')
    @patch('tkinter.Label')
    @patch('tkinter.Button')
    @patch('frontend.gui.on_generate')
    def test_main_function(self, mock_on_generate, mock_button, mock_label, mock_tk):
        """Test the main entry point function"""
        from main import main
        
        # Configure mocks
        mock_app = MagicMock()
        mock_tk.return_value = mock_app
        
        # Call main function
        main()
        
        # Verify Tkinter app was created
        mock_tk.assert_called_once()
        mock_app.title.assert_called_once()
        
        # Verify UI elements were created
        self.assertGreaterEqual(mock_label.call_count, 2)  # At least header and result
        self.assertGreaterEqual(mock_button.call_count, 1)  # At least generate button
        
        # Verify main loop was started
        mock_app.mainloop.assert_called_once()
    
    def test_flask_app_creation(self):
        """Test Flask app creation"""
        from backend.app import create_app
        
        # Create app
        app = create_app()
        
        # Check app configuration
        self.assertEqual(app.name, 'flask_app')
        
        # Check routes are registered
        rule_endpoints = [rule.endpoint for rule in app.url_map.iter_rules()]
        
        # Check core routes
        self.assertIn('home', rule_endpoints)
        self.assertIn('passwords_routes.home', rule_endpoints)
        self.assertIn('passwords_routes.generate_password', rule_endpoints)
        self.assertIn('passwords_routes.test_password', rule_endpoints)
        self.assertIn('voice_routes.register_voice', rule_endpoints)
        self.assertIn('voice_routes.verify_user', rule_endpoints)
    
    @patch('sys.path.append')
    @patch('flask.Flask.run')
    def test_flask_app_running(self, mock_run, mock_path_append):
        """Test running the Flask app from main script"""
        # Create a fake __name__ == "__main__" scenario
        with patch('backend.app.__name__', "__main__"):
            with patch('backend.app.create_app') as mock_create_app:
                # Configure mocks
                mock_app = MagicMock()
                mock_create_app.return_value = mock_app
                
                # Import to execute the module
                import backend.app
                
                # Verify app was created and run
                mock_create_app.assert_called_once()
                mock_app.run.assert_called_once()
                self.assertEqual(mock_app.run.call_args[1]['debug'], True)
    
    @patch('flask.Flask')
    def test_app_blueprints_registered(self, mock_flask):
        """Test that all blueprints are correctly registered"""
        from backend.app import create_app
        
        # Configure mock
        mock_app = MagicMock()
        mock_flask.return_value = mock_app
        
        # Call function
        create_app()
        
        # Verify blueprints were registered
        register_calls = mock_app.register_blueprint.call_args_list
        
        # Extract blueprint arguments
        registered_blueprints = [call[0][0] for call in register_calls]
        
        # Check if we have at least two blueprints (passwords and voice)
        self.assertGreaterEqual(len(registered_blueprints), 2)
    
    @patch('backend.routes.passwords_routes.logging.basicConfig')
    def test_logging_configuration(self, mock_logging_config):
        """Test logging configuration is properly set up"""
        # Import module to execute logging setup
        from backend.routes import passwords_routes
        
        # Verify logging was configured
        mock_logging_config.assert_called_once()
        
        # Check log level
        args = mock_logging_config.call_args[1]
        self.assertEqual(args['level'], passwords_routes.logging.INFO)

if __name__ == "__main__":
    unittest.main()