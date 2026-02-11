import { describe, expect, it } from 'vitest'
import { renderToString } from 'react-dom/server'
import { StaticRouter } from 'react-router-dom/server'
import App from './App'

describe('App', () => {
  it('renders the application title', () => {
    const html = renderToString(
      <StaticRouter location='/'>
        <App />
      </StaticRouter>,
    )

    expect(html).toContain('Narratological Algorithmic Lenses')
  })
})
