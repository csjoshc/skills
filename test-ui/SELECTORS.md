# Playwright Selectors

```javascript
// By label (best for forms)
page.getByLabel('Email')
page.getByLabel('Password', { exact: true })

// By placeholder
page.getByPlaceholder('Search...')

// By text
page.locator('button').filter({ hasText: 'Submit' })
page.locator('summary').filter({ hasText: 'Advanced' })

// By role
page.getByRole('button', { name: 'Save' })
page.getByRole('heading', { name: 'Dashboard' })
page.getByRole('option', { name: 'Dark Mode' })

// By test ID
page.getByTestId('submit-btn')

// CSS
page.locator('.card-header')
page.locator('#main-content')

// Details/Summary (collapsible sections)
page.locator('details').filter({ hasText: 'Section Title' }).locator('summary').click()
```
