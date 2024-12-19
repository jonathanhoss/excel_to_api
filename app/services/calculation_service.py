import os
import formulas


class ExcelCalculationService:
    def __init__(self):
        pass

    def load_excel_model(self, file_path: str) -> formulas.ExcelModel:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found")

        # Load the Excel file
        xl_model = formulas.ExcelModel().loads(file_path)
        return xl_model

    def model_finish(self, xl_model: formulas.ExcelModel) -> formulas.ExcelModel:
        return xl_model.finish()

    def model_calculate(
        self, xl_model: formulas.ExcelModel, inputs: dict = None, outputs: list = None
    ):
        return xl_model.calculate(inputs=inputs, outputs=outputs)

    def get_cell_value(self, xl_model: formulas.ExcelModel, formulas_identifier: str):
        cell: formulas.Ranges = xl_model.get(formulas_identifier)
        return cell.value

    def get_cell_from_solution(
        self,
        solution,
        file_name: str,
        sheet_name: str,
        cell_name: str,
    ):
        key = f"'[{file_name}]{sheet_name}'!{cell_name}"

        print(key)
        cell: formulas.Ranges = solution.get(key)  # z.B. '[abc_excel.xlsx]DATA'!A3

        print(cell.value)

        return cell.value[0].item()


if __name__ == "__main__":
    # Create an instance of the ExcelCalculationService
    service = ExcelCalculationService()

    # Load the Excel file
    file = "test_a.xlsx"

    # get the current working directory
    cwd = os.getcwd()
    file_path = os.path.join(cwd, file)

    print(file_path)

    xl_model = service.load_excel_model(file_path).finish()
    print(service.model_calculate(xl_model))
