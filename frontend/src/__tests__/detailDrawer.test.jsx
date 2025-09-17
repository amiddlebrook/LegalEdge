import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, test, vi } from 'vitest'

import { DetailDrawer } from '../components/DetailDrawer.jsx'

describe('DetailDrawer', () => {
  test('renders children when open and calls onClose', () => {
    const handleClose = vi.fn()
    render(
      <DetailDrawer open title="Test Drawer" onClose={handleClose}>
        <p>drawer body</p>
      </DetailDrawer>,
    )

    expect(screen.getByText('Test Drawer')).toBeInTheDocument()
    expect(screen.getByText('drawer body')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: /close/i }))
    expect(handleClose).toHaveBeenCalledTimes(1)
  })

  test('does not render when open is false', () => {
    render(
      <DetailDrawer open={false} title="Hidden" onClose={() => {}}>
        <p>should not see me</p>
      </DetailDrawer>,
    )

    expect(screen.queryByText('Hidden')).not.toBeInTheDocument()
  })
})