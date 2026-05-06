import io
import time
import pytest


def test_spinner_context_manager_writes_to_stderr():
    from src.ui.output import Spinner
    fake_stderr = io.StringIO()
    # Simulate non-TTY
    fake_stderr.isatty = lambda: False
    with Spinner("Trabajando...", stderr=fake_stderr):
        time.sleep(0.05)
    output = fake_stderr.getvalue()
    assert "Trabajando..." in output


def test_spinner_exits_cleanly():
    from src.ui.output import Spinner
    fake_stderr = io.StringIO()
    fake_stderr.isatty = lambda: False
    try:
        with Spinner("Cargando...", stderr=fake_stderr):
            pass
    except Exception as e:
        pytest.fail(f"Spinner raised exception: {e}")


def test_spinner_non_tty_prints_one_log_line():
    from src.ui.output import Spinner
    fake_stderr = io.StringIO()
    fake_stderr.isatty = lambda: False
    with Spinner("Descargando...", stderr=fake_stderr):
        pass
    output = fake_stderr.getvalue()
    # Should have at least one line with the message (no spinning chars)
    assert "Descargando..." in output


def test_spinner_thread_stops_on_exit():
    from src.ui.output import Spinner
    import threading
    fake_stderr = io.StringIO()
    fake_stderr.isatty = lambda: False
    threads_before = threading.active_count()
    with Spinner("msg", stderr=fake_stderr):
        pass
    threads_after = threading.active_count()
    assert threads_after <= threads_before
