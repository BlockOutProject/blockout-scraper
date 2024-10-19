import pytest
import logging
from errors_handler import handle_errors

def test_handle_errors_sync_function(caplog):
    @handle_errors
    def test_function(x):
        return x / 0  # Provoque une ZeroDivisionError

    with caplog.at_level(logging.ERROR, logger='myvolley'):
        with pytest.raises(ZeroDivisionError):  # On s'attend à ce que l'exception soit levée
            test_function(10)

        # Vérifie que l'erreur a bien été loggée
        assert 'ZeroDivisionError' in caplog.text
        assert 'Erreur dans la fonction synchrone' in caplog.text

@pytest.mark.asyncio
async def test_handle_errors_async_function(caplog):
    @handle_errors
    async def test_async_function(x):
        return x / 0  # Provoque une ZeroDivisionError

    with caplog.at_level(logging.ERROR, logger='myvolley'):
        with pytest.raises(ZeroDivisionError):  # On s'attend à ce que l'exception soit levée
            await test_async_function(10)

        # Vérifie que l'erreur a bien été loggée
        assert 'ZeroDivisionError' in caplog.text
        assert 'Erreur dans la fonction asynchrone' in caplog.text