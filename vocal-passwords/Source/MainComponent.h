#pragma once

#include <JuceHeader.h>

//==============================================================================
class MainComponent : public juce::Component, public juce::Button::Listener
{
public:
    MainComponent(); // Declaration only
    ~MainComponent() override; // Declaration only

    void paint(juce::Graphics& g) override;
    void resized() override;
    void buttonClicked(juce::Button* button) override;

private:
    juce::TextButton generateButton;
    juce::Label passwordLabel;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(MainComponent)
};
