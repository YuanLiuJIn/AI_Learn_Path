import React from 'react'
import { t } from '../i18n.js'
import { Box, Text } from '../ui.js'
import { Pane } from './design-system/Pane.js'
import { Select } from './Select.js'
import { HintLine } from './design-system/HintLine.js'

/**
 * The `/thinking` display dialog: a permission-colored Pane with a bold
 * title, the Shown/Hidden select, and the Enter/Esc hint line.
 */
export function ThinkingToggle({
  currentValue,
  focusIndex,
}: {
  currentValue: boolean
  focusIndex: number
}): React.ReactNode {
  const options = [
    {
      value: 'true',
      label: t('thinking-enabled'),
      description: t('thinking-enabled-desc'),
    },
    {
      value: 'false',
      label: t('thinking-disabled'),
      description: t('thinking-disabled-desc'),
    },
  ]

  return (
    <Pane color="permission">
      <Box flexDirection="column">
        <Box marginBottom={1} flexDirection="column">
          <Text color="remember" bold>
            {t('thinking-title')}
          </Text>
          <Text dimColor>{t('thinking-subtitle')}</Text>
        </Box>

        <Box flexDirection="column" marginBottom={1}>
          <Select
            options={options}
            focusIndex={focusIndex}
            selectedValue={currentValue ? 'true' : 'false'}
            visibleOptionCount={2}
          />
        </Box>
      </Box>
      <Text dimColor italic>
        <HintLine text={t('hint-confirm-exit')} />
      </Text>
    </Pane>
  )
}
