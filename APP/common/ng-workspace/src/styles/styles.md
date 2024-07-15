# Note
Following styles are made under specified guidelines.
Below is a list of classes, examples and instructions on how to use them


### Table of contents:
1. Getting started
2. Content
3. Layout
4. Components
5. Utilities
6. Guidelines


# Getting started
Import  `main.scss` into your app


# Content
### Typography
Predefined classes for font sizes with responsive media queries, font-weights and text alignments

1. Fonts: `font-xxs, font-xs, font-sm, font-md, font-lg, font-title`

2. Font weights: `font-light, font-bold, font-regular`

3. Text alignments: `text-right, text-center, text-left`

4. Text transform: `text-uppercase, text-lowercase, text-capitalize`

5. Vertical alignment: `align-top, align-baseline, align-middle, align-text-top, align-text-bottom,`

6. Colors: `open-data-grey-900, open-data-grey-700, open-data-grey-800, open-data-orange-700, open-data-red-700`

```
<p class="font-xxs"></p>
<p class="font-xs"></p>

<p class="font-sm font-light text-center"></p>
<p class="font-md font-bold text-right"></p>

<span class="align-top open-data-grey-900"></span>
<span class="align-baseline open-data-grey-800"></span>

```


# Layout
Styles for handling layouts: Coordinates, overflows, positions, etc.


# Components
All component specific styles such as buttons, cards, card-groups, can be found in `styles/components/*`


# Utilities

## Breakpoint suffixes
Attach `--xs` for 360 to 539
Attach `--sm` for 540 to 959
Attach `--md` for 960 to 1279
Attach `--lg` for 1280 to 4K
Will be changed later to have a separate suffix for retina displays (1920 to 4K)
Not all classes support the suffixes yet. Will update as and when support is added.

### Display
Showing and hiding elements. Supports breakpoint suffixes.
```
<div class="fx-flex"></div>
<div class="fx-block"></div>
<div class="fx-inline-flex"></div>
<div class="fx-inline-block"></div>
<div class="fx-none"></div>
```

For displaying elements in rows and columns
```
<div class="fx-row"></div>
<div class="fx-column"></div>
```

#### Flex
Parent properties: `flex-direction, flex-wrap, justify-content, align-content, align-items`

Predefined classes

|  Property      | Classes |
|      :--      |    :--   |
| flex-direction | `fx-row, fx-column`  |
| flex-wrap | `flex-wrap, flex-no-wrap` |
| justify-content | `justify-content-start, justify-content-center, justify-content-end, justify-content-around, justify-content-between, justify-content-evenly` |
| align-content | `align-content-start, align-content-center, align-content-end, align-content-around, align-content-between` |
| align-items | `align-item-start, align-item-center, align-item-end, align-baseline`


### Color and background color
* Apply background colors to your elements using classes `open-data-bg-color-name`
```
<div class="open-data-bg-white"></div>
<div class="open-data-bg-blue-400"></div>
<div class="open-data-bg-orange-600"></div>
```

* Apply color to your text elements using classes `open-data-color-name`
```
<span class="open-data-grey-700"></span>
<span class="open-data-grey-800"></span>
<span class="open-data-grey-900"></span>
<span class="open-data-orange-600"></span>
```


### Borders
* Use border utilities to add or remove an element’s borders.
```
<div class="border"></div>
<div class="border-top"></div>
<div class="border-right"></div>
<div class="border-bottom"></div>
<div class="border-left"></div>
```

* Add classes to an element to easily round it's corners.
```
<div class="rounded"></div>
<div class="rounded-top"></div>
<div class="rounded-right"></div>
<div class="rounded-bottom"></div>
<div class="rounded-left"></div>
<div class="rounded-circle"></div>
<div class="rounded-0"></div>
```
Note: `rounded-0` sets `border-radius` to `0`

* Change the border color using border utility classes using `border-color-name`
```
<div class="border-blue-400">
<div class="border-orange-700">
<div class="border-grey-700">
<div class="border-orange-600">
```

List of colors is given at the end.


### Height and width
* Some of the predefined classes for height and width
```
<div class="width-25"></div>
<div class="width-50"></div>
<div class="width-75"></div>
<div class="width-100"></div>
<div class="width-auto"></div>
```
```
<div class="height-25"></div>
<div class="height-50"></div>
<div class="height-75"></div>
<div class="height-100"></div>
<div class="height-auto"></div>
```

### Spacing
* `margin-` for classes that sets margins with suffix `top, right, left, bottom` along with spacer of `4px` ultimately forming classes as `margin-top-1, margin-right-2, margin-bottom-2` and so on.

* Note: Value of spacer is `4px` and adding `0` to class means setting value as 0
```
<span class="margin-top-0"></span>
<span class="margin-right-1"></span>
<span class="margin-left-1"></span>
<span class="margin-bottom-3t"></span>
<span class="margin-x-auto"></span>
<span class="margin-y-auto"></span>
<span class="margin-y-1"></span>
<span class="margin-0"></span>
```

* `padding-` for classes that sets padding and has similar rule as margin. Spacer for padding is `8px`.
```
<span class="padding-top-0"></span>
<span class="padding-right-1"></span>
<span class="padding-left-1"></span>
<span class="padding-bottom-3"></span>
<span class="padding-x-1"></span>
<span class="padding-x-2"></span>
<span class="padding-0"></span>
```

### Z index and shadow
* Predefined classes for `z-index` ranging from value 1 to 24 with related box shadow class attached to it.
Can be used as `z-index-1`
```
<button class="z-index-1"><button>
<nav class="z-index-16"><nav>
```
Stand alone shadow classes without `z-index`
```
<card class="box-shadow-1">/card>
<button class="box-shadow-2"></button>
```

* Specific elements have specified `z-index` as follows:
|   Element   |   Z index  |
|   :--   |    :--    |
| Pop-up, Dialog | 24   |
| Header, Sticky-tabs | 16 |
| Sidebar           | 14 |
|Float buttons | 2 to 4 |
| Buttons, Chips | 0 to 1|

## Available colors
#### Primary Colors

![#blue-400](https://via.placeholder.com/20/378ef0/000000?text=+) blue-400
![#blue-500](https://via.placeholder.com/20/2680eb/000000?text=+) blue-500
![#blue-600](https://via.placeholder.com/20/1473e6/000000?text=+) blue-600
![#blue-700](https://via.placeholder.com/20/0d66d0/000000?text=+) blue-700

![#grey-100](https://via.placeholder.com/20/f4f4f4/000000?text=+) grey-100
![#grey-200](https://via.placeholder.com/20/eeeeee/000000?text=+) grey-200
![#grey-300](https://via.placeholder.com/20/e6e6e6/000000?text=+) grey-300
![#grey-400](https://via.placeholder.com/20/d3d3d3/000000?text=+) grey-400
![#grey-500](https://via.placeholder.com/20/929292/000000?text=+) grey-500
![#grey-600](https://via.placeholder.com/20/777777/000000?text=+) grey-600
![#grey-700](https://via.placeholder.com/20/707070/000000?text=+) grey-700
![#grey-800](https://via.placeholder.com/20/545454/000000?text=+) grey-800
![#grey-900](https://via.placeholder.com/20/232323/000000?text=+) grey-900

![#green-400](https://via.placeholder.com/20/96d681/000000?text=+) green-400
![#green-500](https://via.placeholder.com/20/71b564/000000?text=+) green-500
![#green-600](https://via.placeholder.com/20/51a351/000000?text=+) green-600
![#green-700](https://via.placeholder.com/20/3d994d/000000?text=+) green-700

![#orange-400](https://via.placeholder.com/20/ff8f40/000000?text=+) orange-400
![#orange-500](https://via.placeholder.com/20/fa7832/000000?text=+) orange-500
![#orange-600](https://via.placeholder.com/20/f15a24/000000?text=+) orange-600
![#orange-700](https://via.placeholder.com/20/d93b0b/000000?text=+) orange-700

![#red-400](https://via.placeholder.com/20/ec5b62/000000?text=+) red-400
![#red-500](https://via.placeholder.com/20/e34850/000000?text=+) red-500
![#red-600](https://via.placeholder.com/20/d7373f/000000?text=+) red-600
![#red-700](https://via.placeholder.com/20/c9252d/000000?text=+) red-700


#### Secondary Colors
![#indigo-400](https://via.placeholder.com/20/5c6bc0/000000?text=+) indigo-400
![#indigo-500](https://via.placeholder.com/20/3f51b5/000000?text=+) indigo-500
![#indigo-600](https://via.placeholder.com/20/3949ab/000000?text=+) indigo-600
![#indigo-700](https://via.placeholder.com/20/303f9f/000000?text=+) indigo-700

![#teal-400](https://via.placeholder.com/20/26a69a/000000?text=+) teal-400
![#teal-500](https://via.placeholder.com/20/009688/000000?text=+) teal-500
![#teal-600](https://via.placeholder.com/20/00897b/000000?text=+) teal-600
![#teal-700](https://via.placeholder.com/20/00796b/000000?text=+) teal-700

![#purple-400](https://via.placeholder.com/20/ab47bc/000000?text=+) purple-400
![#purple-500](https://via.placeholder.com/20/9c27b0/000000?text=+) purple-500
![#purple-600](https://via.placeholder.com/20/8e24aa/000000?text=+) purple-600
![#purple-700](https://via.placeholder.com/20/7b1fa2/000000?text=+) purple-700

![#yellow-400](https://via.placeholder.com/20/ffff8d/000000?text=+) yellow-400
![#yellow-500](https://via.placeholder.com/20/ffff00/000000?text=+) yellow-500
![#yellow-600](https://via.placeholder.com/20/ffea00/000000?text=+) yellow-600
![#yellow-700](https://via.placeholder.com/20/ffd600/000000?text=+) yellow-700


# Guidelines

### Common rules for global CSS
1. Is it a global CSS?
  * It will be under global CSS if it's being or will be used in multiple apps
  * Based on the class, it should be placed under styles directory


2. Nomenclature:
  * Prefer meaningful and understandable nomenclature
  * Use full names instead of short forms in case it's a property like `font-sm`
  * Classes which set multiple properties can be a combination of both like `open-data-bg-grey-100`


3. Using ID selectors
  * Prefer using classes instead of id for styles.
  * Use ID selectors to fetch element from DOM


4. Using `!important`
  * Only use !important on page-specific CSS that overrides foreign CSS (from external libraries, like material.scss or other package's css library).
  * Using pseudo selectors and direct parent to override foreign CSS.
  * Let `::ng-deep` and `!important` be the last resort to fix CSS.


### External links
#### [CSS Guidelines](https://developer.mozilla.org/en-US/docs/MDN/Guidelines/Code_guidelines/CSS) <br>

#### [CSS Specificity](https://developer.mozilla.org/en-US/docs/Web/CSS/Specificity)<br>

#### [SCSS playground](https://www.sassmeister.com/)<br>
