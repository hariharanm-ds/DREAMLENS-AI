with open('static/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Replace overview-grid layout to be chat-first full width
old_grid = '''.overview-grid {
  display: grid;
  grid-template-columns: 1.5fr 1.1fr;
  gap: 24px;
  margin-bottom: 24px;
}'''

new_grid = '''.overview-grid {
  display: flex;
  flex-direction: column-reverse;
  gap: 18px;
  margin-bottom: 20px;
}
.dash-card.dream-profile-card {
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
}'''

if old_grid in css:
    css = css.replace(old_grid, new_grid, 1)
    with open('static/style.css', 'w', encoding='utf-8') as f:
        f.write(css)
    print("Updated overview-grid to conversational full-width layout!")
else:
    print("WARNING: old_grid not found.")
