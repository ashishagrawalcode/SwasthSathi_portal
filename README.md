# Medi-X Healthcare Website

A modern, responsive healthcare website built with vanilla HTML, CSS, and JavaScript featuring yellow-green gradient design.

## 🌟 Features

### 🎨 Design
- **Modern UI/UX**: Clean, minimal design with yellow-green gradient color scheme
- **Responsive Design**: Fully responsive across all devices (mobile, tablet, desktop)
- **Smooth Animations**: CSS animations and transitions for enhanced user experience
- **Accessibility**: WCAG compliant with keyboard navigation support

### 🏥 Healthcare Features
- **Appointment Booking**: Modal-based appointment scheduling system
- **BMI Calculator**: Real-time Body Mass Index calculation with health categories
- **Water Intake Tracker**: Daily hydration tracking with visual progress bar
- **Medication Reminders**: Add/remove medication schedules with time management
- **Symptom Checker**: Basic symptom assessment with medical disclaimers

### 🔧 Technical Features
- **Progressive Enhancement**: Works without JavaScript, enhanced with JS
- **Local Storage**: Saves user data (water intake, reminders) locally
- **Form Validation**: Client-side form validation with user feedback
- **Smooth Scrolling**: Navigation with smooth scroll behavior
- **Intersection Observer**: Lazy loading and scroll animations

## 📁 File Structure

```
medi-x/
│
├── index.html          # Main HTML structure
├── styles.css          # All CSS styles and responsive design
├── script.js           # JavaScript functionality
└── README.md          # This file
```

## 🚀 Getting Started

1. **Clone or Download** the files to your local machine
2. **Open** `index.html` in VS Code or your preferred editor
3. **Launch** with Live Server or open directly in browser

## 🎨 Color Palette

The website uses a vibrant yellow-green gradient theme:

- **Primary Yellow**: `#FFD700` (Gold)
- **Primary Green**: `#32CD32` (Lime Green)
- **Gradient Primary**: `linear-gradient(135deg, #FFD700 0%, #32CD32 100%)`
- **Gradient Secondary**: `linear-gradient(135deg, #32CD32 0%, #228B22 100%)`
- **Light Background**: `#F8FFF8` (Very light green)
- **Text Primary**: `#2C3E50` (Dark blue-gray)

## 📱 Sections Overview

### 1. **Header & Navigation**
- Fixed header with backdrop blur effect
- Responsive hamburger menu for mobile
- Smooth scroll navigation with active link highlighting

### 2. **Hero Section**
- Eye-catching gradient background
- Animated floating health cards
- Dual call-to-action buttons
- Responsive grid layout

### 3. **Features Section**
- 4 key features with icons
- Hover effects and animations
- Grid layout with cards

### 4. **Services Section**
- Medical specialties showcase
- Interactive cards with links
- Professional service presentation

### 5. **Health Tools Section**
- Interactive BMI Calculator
- Water Intake Tracker with progress bar
- Medication Reminder system
- Symptom Checker with recommendations

### 6. **Footer**
- Company information and branding
- Quick links and contact details
- Social media integration

## 🛠️ Customization Guide

### Changing Colors
All colors are defined in CSS custom properties (variables) at the top of `styles.css`:

```css
:root {
    --primary-yellow: #FFD700;
    --primary-green: #32CD32;
    --gradient-primary: linear-gradient(135deg, #FFD700 0%, #32CD32 100%);
    /* ... more variables */
}
```

### Adding New Sections
1. Add HTML structure to `index.html`
2. Add corresponding styles to `styles.css`
3. Add JavaScript functionality to `script.js` if needed
4. Update navigation links

### Modifying Health Tools
- **BMI Calculator**: Modify `calculateBMI()` function in `script.js`
- **Water Tracker**: Adjust `waterGoal` variable and related functions
- **Symptom Checker**: Update `getSymptomRecommendations()` function

## 📊 Interactive Features

### BMI Calculator
- Input validation for height and weight
- Real-time calculation with health categories
- Color-coded results with BMI ranges

### Water Tracker
- Daily goal tracking (default: 8 glasses)
- Visual progress bar
- Local storage persistence
- Celebration effects when goal reached

### Medication Reminders
- Add multiple reminders with names and times
- Local storage persistence
- 12-hour time format display
- Easy deletion of reminders

### Symptom Checker
- Keyword-based recommendations
- Medical disclaimer compliance
- Direct appointment booking integration

## 🔧 Browser Compatibility

- **Chrome**: 70+
- **Firefox**: 65+
- **Safari**: 12+
- **Edge**: 80+
- **Mobile Browsers**: iOS 12+, Android 7+

## 📱 Responsive Breakpoints

- **Mobile**: 0px - 480px
- **Tablet**: 481px - 768px
- **Desktop**: 769px+

## ⚡ Performance Features

- **CSS Grid & Flexbox**: Modern layout techniques
- **Intersection Observer**: Efficient scroll animations
- **Lazy Loading**: Images and content optimization
- **Minimal Dependencies**: Only Font Awesome icons
- **Optimized Animations**: Hardware-accelerated transitions

## 🎯 SEO & Accessibility

- **Semantic HTML5**: Proper heading hierarchy and structure
- **Alt Text**: Image descriptions for screen readers
- **ARIA Labels**: Accessibility attributes where needed
- **Keyboard Navigation**: Full keyboard support
- **Focus Management**: Proper focus indicators

## 🚀 Deployment Options

### 1. **Static Hosting** (Recommended)
- Netlify, Vercel, GitHub Pages
- Simply upload all files to hosting service

### 2. **Local Development**
- Use VS Code with Live Server extension
- Python: `python -m http.server 8000`
- Node.js: `npx serve`

## 📝 Customization Examples

### Adding a New Health Tool

1. **HTML Structure** (in `index.html`):
```html

    
        
        Heart Rate Monitor
    
    
        
    

```

2. **JavaScript Function** (in `script.js`):
```javascript
function calculateHeartRate() {
    // Your calculation logic here
}
```

### Modifying the Color Scheme

To change to a blue-purple theme:
```css
:root {
    --primary-yellow: #4A90E2;
    --primary-green: #7B68EE;
    --gradient-primary: linear-gradient(135deg, #4A90E2 0%, #7B68EE 100%);
}
```

## 🐛 Troubleshooting

### Common Issues

1. **Modal not opening**: Check if `script.js` is properly linked
2. **Styles not loading**: Verify `styles.css` path
3. **Icons not showing**: Check Font Awesome CDN connection
4. **Mobile menu not working**: Ensure JavaScript is enabled

### Console Errors
- Check browser console for specific error messages
- Verify all file paths are correct
- Ensure proper HTML structure

## 🔄 Updates & Maintenance

### Regular Updates
- Update Font Awesome CDN link periodically
- Test across different browsers and devices
- Monitor web performance metrics
- Update content and health information as needed

### Adding New Features
1. Plan the feature requirements
2. Design the UI/UX
3. Implement HTML structure
4. Add CSS styles
5. Write JavaScript functionality
6. Test across devices
7. Update documentation

## 📞 Support

For questions or issues:
- Check browser console for errors
- Validate HTML and CSS
- Test in different browsers
- Review responsive design on various screen sizes

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

**Built with ❤️ for better healthcare accessibility**