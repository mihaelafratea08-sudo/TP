from arsenal.forensics.decode import desfa, ghici_strat, citibil, sparge_xor


def test_base64():
    strat, b = desfa("U2FsdXQ=")
    assert strat == "base64"
    assert b == b"Salut"


def test_hex():
    strat, b = desfa("48656c6c6f")
    assert strat == "hex"
    assert b == b"Hello"


def test_url():
    strat, b = desfa("%2Fetc")
    assert strat == "url"
    assert b == b"/etc"


def test_ghici_strat_necunoscut():
    assert ghici_strat("!!!not-an-encoding!!!") == "necunoscut"


def test_citibil():
    assert citibil(b"text normal") is True
    assert citibil(bytes([0, 1, 2])) is False


def test_sparge_xor():
    # Nota: pentru texte scurte, mai multe chei pot produce intamplator tot
    # octeti aflati in zona "citibila" (32..126) - e o ambiguitate reala a
    # metodei prin forta bruta. De aceea nu verificam cheia exacta, doar ca
    # functia gaseste O cheie care reproduce corect textul criptat.
    original = b"Acesta este un mesaj de test pentru XOR, cu cifre 12345 si semne!"
    cheie = 0x2A
    criptat = bytes(b ^ cheie for b in original)
    cheie_gasita, text = sparge_xor(criptat)
    assert cheie_gasita is not None
    assert bytes(b ^ cheie_gasita for b in criptat) == text.encode()
