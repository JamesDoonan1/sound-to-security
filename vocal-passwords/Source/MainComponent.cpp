void MainComponent::buttonClicked(juce::Button* button)
{
    if (button == &generateButton)
    {
        // Backend URL
        juce::URL backendURL("http://127.0.0.1:5000/generate-vocal-password");

        // Prepare POST data
        juce::String jsonPayload = R"({"vocal_input": "test_input"})";

        // Set up InputStreamOptions
        juce::URL::InputStreamOptions options(juce::URL::ParameterHandling::inPostData);
        options = options.withExtraHeaders("Content-Type: application/json");
        options = options.withConnectionTimeoutMs(5000);
        options = options.withBody(jsonPayload);

        // Create input stream for the HTTP request
        std::unique_ptr<juce::InputStream> stream = backendURL.createInputStream(options);

        if (stream != nullptr) // Check if the connection was successful
        {
            // Read the response from the backend
            juce::String response = stream->readEntireStreamAsString();

            // Parse the JSON response
            juce::var parsedResponse = juce::JSON::parse(response);

            if (parsedResponse.isObject())
            {
                // Extract the generated password
                juce::String password = parsedResponse["generated_password"];
                passwordLabel.setText("Generated Password: " + password, juce::dontSendNotification);
            }
            else
            {
                passwordLabel.setText("Error parsing server response", juce::dontSendNotification);
            }
        }
        else
        {
            // Handle connection errors
            passwordLabel.setText("Error connecting to backend", juce::dontSendNotification);
        }
    }
}
