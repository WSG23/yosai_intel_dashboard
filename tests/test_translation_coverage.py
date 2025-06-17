from scripts import check_missing_translations


def test_translations_complete():
    try:
        check_missing_translations.main()
    except SystemExit:
        assert False, "Missing translations"
