# import pytest
# from app.services.external_calculation_service import ExternalCalculationService

# def test_calculate_valid_file(mocker):
#     # Mock the external library
#     mock_calculator = mocker.patch('external_lib.Calculator')
#     mock_calculator.return_value.calculate.return_value = "path/to/result.xlsx"

#     # Mock the result parsing
#     service = ExternalCalculationService()
#     mocker.patch.object(service, '_parse_result_file', return_value={"output_cell_1": 42})

#     # Call the method
#     outputs = service.calculate("path/to/input.xlsx")

#     # Validate results
#     assert outputs == {"output_cell_1": 42}
