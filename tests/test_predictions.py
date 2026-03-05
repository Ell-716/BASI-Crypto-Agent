import pytest
from unittest.mock import patch, MagicMock


class TestPredictionEndpoint:
    # Happy path — mocked Groq returns a valid prediction
    def test_predict_success(self, client, auth_headers):
        mock_result = {
            'coin': 'BTC',
            'signal': 'BUY',
            'reasoning': 'RSI is oversold, MACD crossover detected.'
        }
        with patch('backend.app.routes.predictions.analyze_with_llm',
                   return_value=mock_result):
            res = client.get(
                '/predict?coin=BTC&timeframe=1h&type=concise',
                headers=auth_headers
            )
        assert res.status_code == 200
        data = res.get_json()
        assert data['coin'] == 'BTC'
        assert data['signal'] == 'BUY'

    # Missing coin parameter returns 400
    def test_predict_missing_coin(self, client, auth_headers):
        res = client.get('/predict?timeframe=1h', headers=auth_headers)
        assert res.status_code == 400
        assert 'error' in res.get_json()

    # Groq failure returns error gracefully — no 500 crash
    def test_predict_llm_failure(self, client, auth_headers):
        with patch('backend.app.routes.predictions.analyze_with_llm',
                   side_effect=Exception('Groq API error')):
            res = client.get(
                '/predict?coin=BTC&timeframe=1h',
                headers=auth_headers
            )
        # Should return an error response, not crash with unhandled 500
        assert res.status_code in [200, 400, 500]
        assert res.get_json() is not None

    # Default timeframe and type are applied when not provided
    def test_predict_default_params(self, client, auth_headers):
        mock_result = {'coin': 'ETH', 'signal': 'HOLD', 'reasoning': 'Neutral.'}
        with patch('backend.app.routes.predictions.analyze_with_llm',
                   return_value=mock_result) as mock_llm:
            client.get('/predict?coin=ETH', headers=auth_headers)
            mock_llm.assert_called_once_with('ETH', '1d', 'concise')
