from backend.parsers.grailed import GrailedParser
from backend.parsers.fashionphile import FashionphileParser
from backend.parsers.firstdibs import FirstDibsParser

def test_grailed_parser_extracts_required_fields(grailed_raw):
    parser = GrailedParser()
    product = parser.parse(grailed_raw, "grailed_amiri_apparel_01.json")
    assert product.source_id == "test-grailed-001"
    assert product.brand == "amiri"
    assert product.model == "Amiri Test Shirt"
    assert product.current_price == 425.0
    assert product.source == "grailed"
    assert product.currency == "USD"
    assert product.is_available is True

def test_grailed_parser_marks_sold_item_unavailable(grailed_raw):
    grailed_raw["metadata"]["is_sold"] = True
    parser = GrailedParser()
    product = parser.parse(grailed_raw, "grailed_amiri_apparel_01.json")
    assert product.is_available is False

def test_grailed_parser_derives_category_from_function_id(grailed_raw):
    parser = GrailedParser()
    product = parser.parse(grailed_raw, "grailed_amiri_apparel_01.json")
    assert product.category == "apparel"

def test_fashionphile_parser_maps_category_from_garment_type(fashionphile_raw):
    parser = FashionphileParser()
    product = parser.parse(fashionphile_raw, "fashionphile_tiffany_01.json")
    assert product.category == "jewelry"
    assert product.condition == "Shows Wear"
    assert product.brand == "Tiffany"

def test_fashionphile_parser_uses_currency_field(fashionphile_raw):
    parser = FashionphileParser()
    product = parser.parse(fashionphile_raw, "fashionphile_tiffany_01.json")
    assert product.currency == "USD"

def test_firstdibs_parser_derives_category_from_filename(firstdibs_raw):
    parser = FirstDibsParser()
    product = parser.parse(firstdibs_raw, "1stdibs_chanel_belts_02.json")
    assert product.category == "belts"

def test_firstdibs_parser_availability_from_metadata(firstdibs_raw):
    parser = FirstDibsParser()
    product = parser.parse(firstdibs_raw, "1stdibs_chanel_belts_02.json")
    assert product.is_available is True
    firstdibs_raw["metadata"]["availability"] = "Sold"
    product2 = parser.parse(firstdibs_raw, "1stdibs_chanel_belts_02.json")
    assert product2.is_available is False

def test_firstdibs_parser_extracts_image_from_main_images(firstdibs_raw):
    parser = FirstDibsParser()
    product = parser.parse(firstdibs_raw, "1stdibs_chanel_belts_01.json")
    assert product.image_url == "https://example.com/img.jpg"
