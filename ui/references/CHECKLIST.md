# Testing Checklist and Troubleshooting

## Contents

- Testing checklist
- Troubleshooting

## Testing checklist

### Navigation
- [ ] All routes load
- [ ] Menu/sidebar navigation works
- [ ] Tab switching preserves state
- [ ] Browser back/forward

### Forms
- [ ] Text inputs
- [ ] Select dropdowns
- [ ] Range sliders
- [ ] Checkboxes/toggles
- [ ] Form validation

### Display
- [ ] Empty states
- [ ] Loading states
- [ ] Error handling
- [ ] Data lists

### Interactions
- [ ] Buttons trigger actions
- [ ] Modals
- [ ] Tooltips
- [ ] Theme toggle
- [ ] Collapsible sections (details/summary)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `Cannot find module 'playwright'` | `npm install -D playwright` |
| Browser not installed | `npx playwright install chromium` |
| Page blank | Check frontend is running (`curl <url>`) |
| API 404 | Start backend, check CORS settings |
| Timeout | Increase `timeout: 60000` |
| Selector not found | Use more specific locator |
| Test hangs | Check backend is running |
