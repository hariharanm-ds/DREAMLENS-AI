import re

with open('templates/chat.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update populateScenarioPresets to be tone-aware
old_scenario_fn = '''function populateScenarioPresets(presets, centralEntity) {
    const container = document.getElementById('scenarioPresetsContainer');
    if (!container) return;

    let items = presets;
    if (!items || !items.length) {
      items = [
        `What if I confronted the ${centralEntity} with fearless curiosity?`,
        `What if I befriended or communicated directly with the ${centralEntity}?`,
        `What if I transformed the setting into a sanctuary of golden light?`
      ];
    }'''

new_scenario_fn = '''function populateScenarioPresets(presets, centralEntity) {
    const container = document.getElementById('scenarioPresetsContainer');
    if (!container) return;

    let items = presets;
    if (!items || !items.length) {
      const lower = String(currentDreamText || centralEntity || '').toLowerCase();
      if (/pongal|diwali|festival|harvest|feast|celebrat|wedding|family|pot|rice|sugarcane/.test(lower)) {
        items = [
          `What if the sweet Pongal overflowed into a miraculous feast shared with the entire community?`,
          `What if the golden sunlight bestowed an ancient ancestral blessing of enduring health and prosperity?`,
          `What if you led the family in a joyous dance of thanksgiving that echoed for generations?`
        ];
      } else if (/fly|sky|wings|cloud|soar|glid|bird|mountain/.test(lower)) {
        items = [
          `What if you soared higher into the starlight and unlocked a panoramic view of your future?`,
          `What if you guided others below through the storm from your vantage point in the sky?`,
          `What if the clouds formed an ethereal path leading to an ancient sanctuary?`
        ];
      } else if (/chase|monster|beast|elephant|lion|tiger|run|fear|dark|shadow|threat|danger/.test(lower)) {
        items = [
          `What if I stood my ground with calm awareness and communicated directly with the ${centralEntity}?`,
          `What if I transformed the threat into a powerful protective ally?`,
          `What if I flooded the dark realm with radiant golden light?`
        ];
      } else {
        items = [
          `What if I explored the deeper mystery of the ${centralEntity} with calm curiosity?`,
          `What if I unlocked the hidden potential of this sacred vision?`,
          `What if I transformed the setting into a sanctuary of golden light?`
        ];
      }
    }'''

if old_scenario_fn in text:
    text = text.replace(old_scenario_fn, new_scenario_fn, 1)
    print("Updated populateScenarioPresets with tone awareness!")
else:
    print("WARNING: old_scenario_fn not found.")

# 2. Add updateScenarioTone helper and call it in renderAnalysisResults
scenario_tone_helper = '''
  function updateScenarioTone(dreamText, profile) {
    const lower = String(dreamText || '').toLowerCase();
    const isCelebration = /pongal|diwali|festival|harvest|feast|celebrat|wedding|party|happy|joy|sugarcane|pot|family/.test(lower);
    const isFlight = /fly|sky|wings|cloud|soar|glid|bird|mountain/.test(lower);
    const isThreat = /chase|beast|monster|elephant|lion|tiger|kill|run|fear|dark|shadow|threat|danger/.test(lower);

    const shiftLabel = document.querySelector('.timeline-shift-box .ts-label') || document.querySelector('.timeline-shift-box .ts-label-title');
    const shiftSub = document.querySelector('.timeline-shift-box .ts-subtext') || document.querySelector('.timeline-shift-box .ts-meta-desc');
    const agencyPct = document.getElementById('scenarioAgencyPct') || document.querySelector('.timeline-shift-box .ts-pct');
    const ruleQuote = document.getElementById('scenarioInnerRuleQuote') || document.getElementById('scenarioSovereigntyQuote');
    const takeaway = document.getElementById('scenarioTakeawayText');
    const outcomesList = document.getElementById('scenarioOutcomesList');

    if (isCelebration) {
      if (shiftLabel) shiftLabel.textContent = '✨ Sacred Abundance Multiplier';
      if (agencyPct) agencyPct.textContent = '+95% Fulfillment';
      if (shiftSub) shiftSub.textContent = 'Festive Gratitude: Family Gathering (75%) ➔ Universal Abundance & Harmony (98%)';
      if (ruleQuote) ruleQuote.textContent = 'True abundance multiplies exponentially when celebrated and shared with a grateful heart.';
      if (takeaway) takeaway.textContent = 'Sharing blessings and practicing daily gratitude anchors festive joy into enduring waking peace.';
      if (outcomesList) {
        outcomesList.innerHTML = `
          <div class="outcome-item"><span>🌾</span><span>Deeper emotional connection with family and cultural roots</span></div>
          <div class="outcome-item"><span>🍯</span><span>Overflowing sense of gratitude, abundance, and inner peace</span></div>
          <div class="outcome-item"><span>☀️</span><span>Renewed solar vitality for positive creative beginnings</span></div>
          <div class="outcome-item"><span>✨</span><span>Effortless multiplication of health, happiness, and shared joy</span></div>
        `;
      }
    } else if (isFlight) {
      if (shiftLabel) shiftLabel.textContent = '🕊️ Panoramic Consciousness Shift';
      if (agencyPct) agencyPct.textContent = '+88% Perspective';
      if (shiftSub) shiftSub.textContent = 'Grounded Outlook (30%) ➔ Panoramic Transcendence (95%)';
      if (ruleQuote) ruleQuote.textContent = 'Elevating your vantage point dissolves waking friction and reveals the broader horizon.';
      if (takeaway) takeaway.textContent = 'Zooming out from temporary conflicts allows effortless navigation through life transitions.';
      if (outcomesList) {
        outcomesList.innerHTML = `
          <div class="outcome-item"><span>🕊️</span><span>Liberation from petty daily anxieties and emotional clutter</span></div>
          <div class="outcome-item"><span>🏔️</span><span>Clarity of long-term vision and purpose</span></div>
          <div class="outcome-item"><span>🌌</span><span>Effortless emotional buoyancy and mental freedom</span></div>
          <div class="outcome-item"><span>✨</span><span>High confidence and sovereign decision-making</span></div>
        `;
      }
    } else if (isThreat) {
      if (shiftLabel) shiftLabel.textContent = '🛡️ Conscious Sovereignty Shift';
      if (agencyPct) agencyPct.textContent = '+82% Agency';
      if (shiftSub) shiftSub.textContent = 'Original Reaction: Hesitation & Defense (25%) ➔ Empowered Standoff: Sovereign Command (92%)';
      if (ruleQuote) ruleQuote.textContent = 'Facing the unknown with conscious calm transmutes perceived threats into creative allies.';
      if (takeaway) takeaway.textContent = 'Choosing calm presence over avoidance converts subconscious anxiety into sovereign authority.';
      if (outcomesList) {
        outcomesList.innerHTML = `
          <div class="outcome-item"><span>🛡️</span><span>Heightened courage and assertive self-command</span></div>
          <div class="outcome-item"><span>⚡</span><span>Clear personal boundaries in high-pressure waking situations</span></div>
          <div class="outcome-item"><span>👑</span><span>Integration of deep instinctual power without fear</span></div>
          <div class="outcome-item"><span>🌟</span><span>Dissolution of chronic worry into grounded resilience</span></div>
        `;
      }
    }
  }
'''

if 'function updateScenarioTone(' not in text:
    idx_sc = text.find('function populateScenarioPresets(')
    text = text[:idx_sc] + scenario_tone_helper + '\n  ' + text[idx_sc:]
    print("Added updateScenarioTone function!")

# Call updateScenarioTone inside renderAnalysisResults
target_call = 'populateScenarioPresets(data.scenario_presets, symbolNet?.center_node?.label || profile.key_symbols?.[0] || \'Encounter\');'
replacement_call = '''populateScenarioPresets(data.scenario_presets, symbolNet?.center_node?.label || profile.key_symbols?.[0] || 'Encounter');
    updateScenarioTone(dreamText, profile);'''

if target_call in text and 'updateScenarioTone(dreamText' not in text:
    text = text.replace(target_call, replacement_call, 1)
    print("Hooked updateScenarioTone into renderAnalysisResults!")

# 3. Update Archetype Label logic in renderAnalysisResults
old_arch_logic = "if (/rain|storm|umbrella/.test(lower)) archLabel.textContent = '⚡ The Storm Conductor';"
new_arch_logic = """if (/pongal|diwali|festival|harvest|feast|celebrat|wedding|family/.test(lower)) archLabel.textContent = '🌾 The Abundant Harvester';
      else if (/rain|storm|umbrella/.test(lower)) archLabel.textContent = '⚡ The Storm Conductor';"""

if old_arch_logic in text:
    text = text.replace(old_arch_logic, new_arch_logic, 1)
    print("Updated archetype label with celebration / Pongal case!")

with open('templates/chat.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Saved templates/chat.html successfully.")
