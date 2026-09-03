<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref } from 'vue'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

// Design read (design-taste-frontend):
//   "Reading this as: B2B SaaS landing for robotics engineers, with a
//    dark-tech / mission-control language, leaning toward native CSS tokens
//    + GSAP scroll motion. No new colour beyond the blue/amber accent family."
gsap.registerPlugin(ScrollTrigger)

const root = ref<HTMLElement | null>(null)
const ctx = ref<gsap.Context | null>(null)

const stats = [
  { value: '12+', label: 'Robot families orchestrated' },
  { value: '60 Hz', label: 'Closed-loop control rate' },
  { value: '99.95%', label: 'Digital-twin sync uptime' },
  { value: '<8 ms', label: 'Command round-trip' },
]

const pillars = [
  {
    title: 'Unified control plane',
    body: 'One API for arms, grippers, mobile bases and humanoids. Compose behaviours, not boilerplate.',
    tag: 'ORCHESTRATION',
  },
  {
    title: 'Physics-accurate twin',
    body: 'A live digital twin mirrors every joint. Validate a plan in simulation before a single actuator moves.',
    tag: 'SIMULATION',
  },
  {
    title: 'Skill-first authoring',
    body: 'Capture a motion once as a reusable skill. Replay it across fleets with drift correction built in.',
    tag: 'SKILLS',
  },
  {
    title: 'Observability by default',
    body: 'Telemetry, joint state and fault traces stream over a typed contract. Watch the machine think.',
    tag: 'TELEMETRY',
  },
]

onMounted(() => {
  if (!root.value) return
  ctx.value = gsap.context(() => {
    // Hero entrance: staggered, calm (motion dial ~6, not cinematic).
    gsap.from('.hero-stagger', {
      y: 22,
      opacity: 0,
      duration: 0.7,
      ease: 'power2.out',
      stagger: 0.08,
    })

    // Scroll reveals for every .reveal block.
    gsap.utils.toArray<HTMLElement>('.reveal').forEach((el) => {
      ScrollTrigger.create({
        trigger: el,
        start: 'top 82%',
        once: true,
        onEnter: () => el.classList.add('is-in'),
      })
    })
  }, root.value)
})

onBeforeUnmount(() => {
  ctx.value?.revert()
})
</script>

<template>
  <div ref="root" class="taste theme-dark rcs-landing" data-variance="8" data-motion="6" data-density="4">
    <!-- HUD grid backdrop, reuses existing --hud-grid token -->
    <div class="hud-grid" aria-hidden="true" />

    <!-- ============ HERO ============ -->
    <header class="hero">
      <span class="tech-label hero-stagger">ROBOT CONTROL SYSTEM // v2.2</span>
      <h1 class="display hero-stagger">
        Teach one robot.<br />Command the whole fleet.
      </h1>
      <p class="hero-sub hero-stagger">
        RCS is the mission-control layer for autonomous manipulation: a single
        control plane, a physics-accurate digital twin, and skills you author
        once and replay anywhere.
      </p>
      <div class="hero-cta hero-stagger">
        <a class="btn btn-primary" href="#start">Request access</a>
        <a class="btn btn-ghost" href="#pillars">See how it works</a>
      </div>

      <dl class="hero-stats hero-stagger">
        <div v-for="s in stats" :key="s.label" class="stat corner-tick">
          <dt class="stat-value">{{ s.value }}</dt>
          <dd class="tech-label">{{ s.label }}</dd>
        </div>
      </dl>
    </header>

    <!-- ============ PILLARS (asymmetric bento, not 3 equal cards) ============ -->
    <section id="pillars" class="pillars reveal">
      <span class="tech-label">WHAT YOU GET</span>
      <h2 class="display">Four parts, one surface.</h2>
      <div class="bento">
        <article
          v-for="p in pillars"
          :key="p.title"
          class="glass-panel card corner-tick"
        >
          <span class="tech-label">{{ p.tag }}</span>
          <h3 class="card-title">{{ p.title }}</h3>
          <p class="card-body">{{ p.body }}</p>
        </article>
      </div>
    </section>

    <!-- ============ CTA ============ -->
    <section id="start" class="cta reveal">
      <div class="glass-panel cta-panel corner-tick">
        <h2 class="display">Bring your cell online.</h2>
        <p>
          Point RCS at your robots and ship a controlled behaviour before
          lunch. No firmware fork required.
        </p>
        <a class="btn btn-primary" href="#start">Talk to engineering</a>
      </div>
    </section>

    <footer class="foot">
      <span class="tech-label">RCS // BUILT WITH design-taste-frontend</span>
    </footer>
  </div>
</template>

<style scoped>
.rcs-landing {
  position: relative;
  min-height: 100%;
  padding: clamp(48px, 7vw, 120px) clamp(20px, 6vw, 96px);
  overflow: hidden;
}

.hud-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(var(--hud-grid) 1px, transparent 1px),
    linear-gradient(90deg, var(--hud-grid) 1px, transparent 1px);
  background-size: var(--hud-grid-size) var(--hud-grid-size);
  pointer-events: none;
  mask-image: radial-gradient(circle at 50% 0%, #000 0%, transparent 75%);
}

/* ---- Hero ---- */
.hero {
  position: relative;
  max-width: 1080px;
  margin: 0 auto;
  text-align: left;
}

.hero h1 {
  font-size: clamp(40px, 6.4vw, 84px);
  margin: 18px 0 22px;
  background: linear-gradient(180deg, var(--fg) 30%, var(--accent-hover) 140%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.hero-sub {
  max-width: 56ch;
  color: var(--fg-secondary);
  font-size: clamp(15px, 1.4vw, 18px);
  line-height: 1.6;
}

.hero-cta {
  display: flex;
  gap: 14px;
  margin: 30px 0 48px;
  flex-wrap: wrap;
}

/* .btn / .btn-primary / .btn-ghost now live in global.css (brand primitives)
   so every page shares the same CTA language. */

/* Stats row: asymmetric, tracked, HUD-styled */
.hero-stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: clamp(14px, 2vw, 28px);
  margin: 0;
  padding-top: 12px;
  border-top: 1px solid var(--divider);
}

.stat {
  padding: 16px 18px;
  background: var(--bg-surface);
  border-radius: var(--radius);
}

.stat-value {
  font-family: var(--font-display);
  font-size: clamp(22px, 2.6vw, 34px);
  margin: 0;
  color: var(--fg);
}

.stat dd {
  margin: 6px 0 0;
}

/* ---- Pillars ---- */
.pillars {
  position: relative;
  max-width: 1180px;
  margin: clamp(64px, 9vw, 130px) auto 0;
}

.pillars h2 {
  font-size: clamp(28px, 3.6vw, 46px);
  margin: 12px 0 36px;
}

.card {
  padding: clamp(20px, 2vw, 30px);
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 200px;
  transition: transform var(--transition), border-color var(--transition);
}

.card:hover {
  transform: translateY(-4px);
  border-color: var(--accent);
}

.card-title {
  font-family: var(--font-display);
  font-size: clamp(18px, 1.8vw, 23px);
  margin: 4px 0 0;
  color: var(--fg);
}

.card-body {
  color: var(--fg-secondary);
  line-height: 1.6;
  margin: 0;
}

/* ---- CTA ---- */
.cta {
  position: relative;
  max-width: 1180px;
  margin: clamp(64px, 9vw, 130px) auto 0;
}

.cta-panel {
  padding: clamp(32px, 4vw, 56px);
  text-align: center;
  margin-left: var(--taste-offset);
}

.cta-panel h2 {
  font-size: clamp(28px, 3.4vw, 44px);
  margin: 0 0 14px;
}

.cta-panel p {
  color: var(--fg-secondary);
  max-width: 52ch;
  margin: 0 auto 26px;
}

.foot {
  max-width: 1180px;
  margin: 64px auto 0;
  text-align: center;
  opacity: 0.7;
}

@media (max-width: 720px) {
  .hero-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
