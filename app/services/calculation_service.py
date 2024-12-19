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
    ) -> formulas.ExcelModel:
        return xl_model.calculate(inputs=inputs, outputs=outputs)


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
