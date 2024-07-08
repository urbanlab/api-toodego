# Prediction interface for Cog ⚙️
# https://cog.run/python

from cog import BasePredictor, Input, Path
import os

AUTH_TOKEN = os.getenv('AUTH_TOKEN')

class Predictor(BasePredictor):
    def setup(self) -> None:
        """Load the model into memory to make running multiple predictions efficient"""
        # self.model = torch.load("./weights.pth")

    def predict(
        self,
        test: str = Input(description="Image file to run through the model"),
        authToken: str = Input(description="Auth Token"),
    ) -> str:
        print("Auth token: ", AUTH_TOKEN)
        if authToken != AUTH_TOKEN:
            return "Invalid auth token"
        """Run a single prediction on the model"""
        # processed_input = preprocess(image)
        # output = self.model(processed_image, scale)
        # return postprocess(output)
        return test
